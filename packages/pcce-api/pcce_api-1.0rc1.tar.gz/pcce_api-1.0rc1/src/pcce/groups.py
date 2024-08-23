"""
Groups
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.groups import GroupSchema


class GroupsAPI(APIEndpoint):
    """Groups"""

    _path = "api/v1/groups"

    def list(self) -> list[dict]:
        """
        Retrieves the list of all groups.

        Example:
            >>> pcce.groups.list()
        """
        return self._get()

    def list_names(self) -> list[str]:
        """
        Retrieves a list of all group names as an array of strings.

        Example:
            >>> pcce.groups.list_names()
        """
        return self._get("names")

    def create(self, data: dict) -> None:
        """
        Creates a group with users.

        Args:
            data (dict): Group data

        Example:
            >>> pcce.groups.create()
        """
        schema = GroupSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post(json=validated_data)

    def delete(self, _id: str) -> None:
        """
        Deletes a group.

        Args:
            id (str): Group name.

        Example:
            >>> pcce.groups.delete('string')
        """
        self._delete(f"{_id}")

    def update(self, _id: str, data: dict) -> None:
        """
        Creates or modifies a group.

        Args:
            _id (str): Group name.
            data (dict): Group data

        Example:
            >>> pcce.groups.update()
        """
        schema = GroupSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._put(f"{_id}", json=validated_data)
