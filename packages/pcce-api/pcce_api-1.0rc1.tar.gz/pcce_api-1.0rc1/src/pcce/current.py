"""
Current
"""

from __future__ import annotations

from restfly import APIEndpoint


class CurrentAPI(APIEndpoint):
    """Current"""

    _path = "api/v1/current"

    def list_collections(self) -> list[dict]:
        """
        Returns collections in the current project that the user has permission to access.

        Example:
            >>> pcce.current.list_collections()
        """
        return self._get("collections")

    def list_projects(self) -> list[dict]:
        """
        Gets current user projects.

        Example:
            >>> pcce.current.list_projects()
        """
        return self._get("projects")
