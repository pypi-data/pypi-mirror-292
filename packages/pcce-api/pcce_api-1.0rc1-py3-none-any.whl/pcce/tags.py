"""
Tags
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.tags import TagSchema, VulnTagSchema


class TagsAPI(APIEndpoint):
    """Tags"""

    _path = "api/v1/tags"

    def list(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves a list of tags.

        Args:
            params (dict): Query parameters
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = TagSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def add(self, data: dict) -> None:
        """
        Creates a tag that helps you manage the vulnerabilities in your environment.

        Args:
            data (dict): Tag data.
        """
        schema = TagSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post(json=validated_data)

    def delete(self, _id: str) -> None:
        """
        Deletes a tag from the system.

        Args:
            _id (str): Name of tag to delete.
        """
        self._delete(f"{_id}")

    def update(self, _id: str, data: dict) -> None:
        """
        Updates the parameters in a given tag.

        Args:
            _id (str): Name of tag to update.
            data (dict): Tag data.
        """
        schema = TagSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._put(f"{_id}", json=validated_data)

    def delete_vuln(self, _id: str) -> None:
        """
        Removes a tag from a vulnerability

        Args:
            _id (str): Name of vul tag to delete.
        """

        self._delete(f"{_id}/vuln")

    def set_vuln(self, _id: str, vuln_data: dict) -> None:
        """
        Sets a tag to a vulnerability based on Common Vulnerability and Exposures (CVE) ID, package, and resource.

        Args:
            _id (str): Name of vul tag to add.
            data (dict): Vul tag data.
        """
        schema = VulnTagSchema()
        errors = schema.validate(vuln_data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(vuln_data))
        self._post(f"{_id}/vuln", json=validated_data)
