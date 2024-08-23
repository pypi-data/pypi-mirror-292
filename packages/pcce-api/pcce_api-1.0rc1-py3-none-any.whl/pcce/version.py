"""
Version
"""

from __future__ import annotations

from restfly import APIEndpoint


class VersionAPI(APIEndpoint):
    """
    Version
    """

    _path = "api/v1/version"

    def get(self) -> str:
        """
        Retrieves the version number for Console
        """
        return self._get()
