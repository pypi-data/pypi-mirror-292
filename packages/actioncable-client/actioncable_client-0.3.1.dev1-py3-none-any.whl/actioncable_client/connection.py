# Copyright 2024 Liant SASU
#
# License: MIT
# See: LICENSE file at root of the repository
#
# Author: Roland Laurès <roland@liant.dev>
"""
ActionCable connection.
"""

from .subscription import Subscription

from typing import Any, Callable, Union

import threading
import uuid
import json
import logging
import time
import websocket
from requests_oauth2client import BaseOAuth2RenewableTokenAuth
from requests.auth import AuthBase

class Connection:
    """
    The connection to a ActionCable capable server
    """
    def __init__(self, url: str,
                 auth: Union[AuthBase, Callable[[], Union[list[str], dict[str, str]]], None] = None,
                 origin: Union[str, None] = None,
                 header: Union[None, list[str], dict[str, str]] = None,
                 send_pong=False):
        """
        :param url: The url of the ActionCable capable server.
        :param auth: (Optional) The AuthBase use with websocket opening to authenticate.
        :param origin: (Optional) A origin to be used as origin at the Websocket connection).
                                  With a auth object, the base URL of the auth object will be
                                  used by default.
        :param header: (Optional) custom header for websocket handshake.

        You can choose to use either auth, header for authentication.
        But we recommend that you use the auth with a OAuth2Client instance already configured
        that will provide the access_tocken and allow auto-renew.
        """
        self.logger = logging.getLogger('ActionCable::Connection')

        self.url = url
        self.auth = auth
        self._log_ping: bool = False
        self.origin: Union[str, None] = None
        if origin is None:
            if isinstance(self.auth, BaseOAuth2RenewableTokenAuth):
                from urllib.parse import urlparse
                auth_url = urlparse(self.auth.client.token_endpoint)
                self.origin = f"{auth_url.scheme}://{auth_url.netloc}"
        else:
            self.origin = origin
        self.header = header
        self.send_pong = send_pong

        self.subscriptions: dict[str, Subscription] = {}

        self.websocket: Union[websocket.WebSocketApp, None] = None
        self.ws_thread: Union[threading.Thread, None] = None

        self.auto_reconnect = False


    def connect(self) -> None:
        """
        Connects to the server.
        """
        self.logger.debug('Establishing connection...')

        if self.connected:
            self.logger.warning('Connection already established. Return...')
            return

        self.auto_reconnect = True

        self.ws_thread = threading.Thread(
            name="APIConnectionThread_{}".format(uuid.uuid1()),
            target=self._run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def disconnect(self) -> None:
        """
        Closes the connection.
        """
        self.logger.debug('Close connection...')

        self.auto_reconnect = False

        if self.websocket is not None:
            self.websocket.close()

    def _run_forever(self) -> None:
        while self.auto_reconnect:
            try:
                self.logger.debug('Run connection loop.')

                header: Union[list[str], dict[str, str], Callable[[], Any]] = []
                if self.auth is not None:
                    if isinstance(self.auth, AuthBase):
                        from requests import Request
                        req = Request('GET', url=self.origin)
                        r = req.prepare()
                        r = self.auth(r)
                        header = dict(r.headers)
                    else:
                        header = self.auth()
                elif self.header is not None:
                    header = self.header

                self.websocket = websocket.WebSocketApp(
                    self.url, header=header, on_message=self._on_message,
                    on_close=self._on_close, on_open=self._on_open
                )

                if self.origin is None:
                    self.websocket.run_forever()
                else:
                    self.websocket.run_forever(origin=self.origin)
            except Exception as exc:
                self.logger.error('Connection loop raised exception. Exception: %s', exc)
            time.sleep(1) # release the hand to other threads

    def send(self, data: dict[str, Any]) -> None:
        """
        Sends data to the server.
        """
        self.logger.debug('Send data: {}'.format(data))

        if self.websocket is None or not self.connected:
            self.logger.warning('Connection not established. Return...')
            return

        self.websocket.send(json.dumps(data))

    def _on_open(self, _socket: websocket.WebSocket) -> None:
        """
        Called when the connection is open.
        """
        self.logger.debug('Connection established.')


    def _on_message(self, _socket: websocket.WebSocket, message: Any) -> None:
        """
        Called aways when a message arrives.
        """
        if isinstance(message, str):
            data = json.loads(message)
        else:
            data = message
        message_type = None
        identifier = None
        subscription = None

        if 'type' in data:
            message_type = data['type']

        if 'identifier' in data:
            identifier = json.loads(data['identifier'])

        if identifier is not None:
            subscription = self.find_subscription(identifier)

        if subscription is not None:
            subscription.received(data)
        elif message_type == 'welcome':
            self.logger.debug('Welcome message received.')

            for subscription in self.subscriptions.values():
                if subscription.state == 'connection_pending':
                    subscription.create()

        elif message_type == 'ping':
            if self.log_ping:
                self.logger.debug('Ping received.')
            if self.send_pong:
                self.send({'command': 'pong'})
        else:
            self.logger.warning('Message not supported. (Message: {})'.format(message))

    def _on_close(self, socket: websocket.WebSocket, status_code: Any, msg: Any) -> None:
        """
        Called when the connection was closed.
        """
        self.logger.debug('Connection closed (%s: %s).', str(status_code), str(msg))

        for subscription in self.subscriptions.values():
            if subscription.state == 'subscribed':
                subscription.state = 'connection_pending'

    def get_log_ping(self) -> bool:
        return self._log_ping
    def set_log_ping(self, value: bool):
        self._log_ping = value
    log_ping = property(get_log_ping, set_log_ping)
    """  If true every ping gets logged (Default: False).
    """

    @property
    def socket_present(self) -> bool:
        """
        If socket is present.
        """
        return self.websocket is not None and self.websocket.sock is not None

    @property
    def connected(self) -> bool:
        """
        If connected to server.
        """
        return self.websocket is not None and \
               self.websocket.sock is not None and \
               self.websocket.sock.connected

    def find_subscription(self, identifier) -> Union[Subscription, None]:
        """
        Finds a subscription
        by it's identifier.
        """
        for subscription in self.subscriptions.values():
            if subscription.identifier == identifier:
                return subscription
        return None
