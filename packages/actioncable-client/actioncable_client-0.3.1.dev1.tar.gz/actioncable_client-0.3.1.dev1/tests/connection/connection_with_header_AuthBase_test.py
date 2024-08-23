# Copyright 2024 Liant SASU
#
# License: MIT
# See: LICENSE file at root of the repository
#
# Author: Roland Laurès <roland@liant.dev>
"""
Here we intend to test the behavior when setting manually the headers field
of the Connection object
"""


import pytest
from pytest_mock import MockFixture

from callee import StartsWith # type: ignore
from time import sleep
import threading
import websocket
import logging

from actioncable_client.connection import Connection # type: ignore

# This is an example with a OAuth2DeviceCodeAuth, but any other Auth method
# will work.
@pytest.fixture
def auth(mocker: MockFixture):
    from requests import Request
    from requests.structures import CaseInsensitiveDict
    mocker.patch('requests_oauth2client.OAuth2DeviceCodeAuth', autospec=True)
    from requests_oauth2client import OAuth2Client, OAuth2DeviceCodeAuth, DeviceAuthorizationResponse
    req = Request('GET', 'http://example.com/oauth/token') # nosemgrep: request-with-http
    r = req.prepare()
    r.headers = CaseInsensitiveDict(data={ 'Authorization': 'Bearer XXXX' })

    # Mock OAuth2Client
    mock_client = mocker.MagicMock(spec=OAuth2Client)
    mock_client.token_endpoint = 'http://example.com/oauth/token' # nosec B105
    mock_client.client_id = 'application_id'
    mock_client.device_authorization_endpoint = 'http://example.com/oauth/authorize_device'

    # Mock the authorize_device method
    mock_device_auth_resp = mocker.MagicMock(spec=DeviceAuthorizationResponse)
    mock_device_auth_resp.device_code = 'fake_device_code'
    mock_device_auth_resp.user_code = 'fake_user_code'
    mock_device_auth_resp.verification_uri = 'http://example.com/verify'
    mock_device_auth_resp.expires_in = 1800
    mock_device_auth_resp.interval = 5

    mock_client.authorize_device.return_value = mock_device_auth_resp

    # Create the OAuth2DeviceCodeAuth instance with the mocked client and response
    obj = OAuth2DeviceCodeAuth(mock_client, mock_device_auth_resp)
    obj.client = mock_client
    obj.return_value = r # type: ignore
    return obj


@pytest.fixture
def connection(auth) -> Connection:
    conn = Connection('ws://example.com/cable', auth=auth)
    conn.logger.setLevel(logging.DEBUG)
    return conn


def test_instantiation(connection: Connection):
    assert connection is not None

def test_connect_should_start_run_forever_thread(connection: Connection, mocker: MockFixture):
    mocker.patch('threading.Thread', spec=threading.Thread)
    assert connection.auto_reconnect is False
    assert connection.ws_thread is None
    connection.connect()
    threading.Thread.assert_called_once_with(name=StartsWith('APIConnectionThread_'), target=connection._run_forever) # type: ignore
    assert connection.auto_reconnect is True
    assert connection.ws_thread.daemon is True
    connection.ws_thread.start.assert_called_once()

def test_run_forever_should_create_WS_and_call_run_forever(connection: Connection, mocker: MockFixture):
    mocker_class = mocker.patch('websocket.WebSocketApp', spec=websocket.WebSocketApp)
    connection.auto_reconnect = True
    assert connection.websocket is None
    connection.connect()
    sleep(0.001) # ensure _run_forever is called

    connection.auth.assert_called_once()
    websocket.WebSocketApp.assert_called_once_with( # type: ignore
        'ws://example.com/cable',
        on_message=connection._on_message, on_close=connection._on_close, on_open=connection._on_open,
        header={ 'Authorization': 'Bearer XXXX' }
    )
    assert isinstance(connection.websocket, mocker_class.__class__)
    # No ping because already managed by server side.
    connection.websocket.run_forever.assert_called_once_with(origin='http://example.com') # type: ignore
    # finish the loop.
    connection.disconnect()
