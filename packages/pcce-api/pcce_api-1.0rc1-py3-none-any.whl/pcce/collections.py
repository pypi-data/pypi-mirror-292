"""
Collections
"""

from __future__ import annotations

from restfly import APIEndpoint
from restfly.utils import dict_clean

from .schema.collections import CollectionSchema


class CollectionsAPI(APIEndpoint):
    """Collections"""

    _path = "api/v1/collections"

    def list(self, exclude_prisma: bool | None = None) -> list[dict]:
        """
        Retrieves a list of all collections.

        Args:
            exclude_prisma (bool): ExcludePrisma indicates to exclude Prisma collections.

        Example:
            >>> pcce.collections.list()
        """
        return self._get(params=dict_clean({"excludePrisma": exclude_prisma}))

    def create(self, data: dict) -> None:
        """
        Creates a new collection.

        Args:
            data (dict): Collection data.

        Example:
            pcce.collection.create()
        """
        schema = CollectionSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post(json=validated_data)

    def delete(self, name: str) -> None:
        """
        Deletes a collection.

        Args:
            name (str): Collection name. Must be unique.

        Example:
            pcce.collections.delete('my-collection)
        """
        self._delete(f"{name}")

    def update(self, name: str, data: dict) -> None:
        """
        Updates the parameters for a specific collection.

        Args:
            name (str): Collection name. Must be unique.
            data (dict): Collection data.

        Example:
            pcce.collection.update()
        """
        schema = CollectionSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._put(f"{name}", json=validated_data)

    def get_policy(self, name: str) -> list[dict]:
        """
        Retrieves all policies that uses a specified collection.

        Example:
            >>> pcce.collections.get_policy('my-collection')
        """
        return self._get(f"{name}/usages")
