# Copyright 2024 Liant SASU
#
# License: MIT
# See: LICENSE file at root of the repository
#
# Author: Roland Laurès <roland@liant.dev>
"""
ActionCable base channel class module.
"""

from .connection import Connection
from .subscription import Subscription
from .message import Message

from typing import Callable, Union, Any

class ActionBaseChannel:
    """
    Define your Channel class by inherit from this class.
    Then implement the actions you want to be called.
    """
    def __init__(self, connection: Connection, on_unkonwn_action_message: Union[Callable[[Message], None], None] = None):
        """
        :param connection: The connection which will be use for the subscriptions
        :param on_message: Called with the messages that are not actions (without action filed defined)
                           or when the action is not defined.
        """
        self._connection = connection
        self.on_unkonwn_action_message = on_unkonwn_action_message
        self._subscription  = Subscription(self._connection, { 'channel': self.__class__.__name__ })
        self._subscription.on_receive(self._on_receive)

    def _on_receive(self, message: Message) -> None:
        if hasattr(self, message.action):
            getattr(self, message.action)(**message.data)
        else:
            self._connection.logger.debug(f"{self.__class__.__name__}: action not found ({message.action})")
            if self.on_unkonwn_action_message is not None:
                self.on_unkonwn_action_message(message)

    def transmit(self, action: str, data: dict[str, Any]):
        self._subscription.send(Message(action=action, data=data))
