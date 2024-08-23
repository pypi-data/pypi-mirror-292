# Copyright 2024 Liant SASU
#
# License: MIT
# See: LICENSE file at root of the repository
#
# Author: Roland Laurès <roland@liant.dev>
"""
ActionCable message
"""

import json
from typing import Any


class Message:
    """
    A subscription message.
    """
    def __init__(self, action: str, data: dict[str, Any]):
        self.action = action
        self.data = data

    def message(self):
        """
        The message properly
        formatted.
        """
        message = self.data
        message['action'] = self.action
        return message

    def raw_message(self):
        """
        The message formatted
        and dumped.
        """
        return json.dumps(self.message())
