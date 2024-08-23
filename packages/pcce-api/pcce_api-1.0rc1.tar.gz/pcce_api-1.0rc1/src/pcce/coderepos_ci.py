"""
CodeRepo CI
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.coderepos_ci import CodereposCISchema


class CodereposCIAPI(APIEndpoint):
    """CodeRepo CI"""

    _path = "api/v1/coderepos-ci"

    def add(self, data: dict | None = None) -> None:
        """
        Adds a CI code repository scan result.

        Args:
            data (dict): CI code repository scan result data

        Example:
            >>> pcce.coderepos_ci.add()
        """
        schema = CodereposCISchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        return self._post(json=validated_data)

    def resolve(self, data: dict) -> None:
        """
        Adds vulnerability data for the given code repo scan result.

        Args:
            data (dict): CI code repository scan result data

        Example:
            >>> pcce.coderepos_ci.resolve()
        """
        schema = CodereposCISchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        return self._post("evaluate", json=validated_data)
