"""
Ping
"""

from __future__ import annotations

from restfly import APIEndpoint


class PingAPI(APIEndpoint):
    """Ping"""

    _path = "api/v1/_ping"

    def _ping(self) -> None:
        """
        Checks if Console is reachable from your network host.
        """
        self._get()
