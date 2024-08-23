"""
Credentials
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.credentials import CredentialSchema, CredentialsParamsSchema


class CredentialsAPI(APIEndpoint):
    """Credentials"""

    _path = "api/v1/credentials"

    def list(self, params: dict | None = None) -> list:
        """
        Retrieves a list of all credentials from the credentials store.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.credentials.list()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = CredentialsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def add(self, data: dict) -> None:
        """
        Updates a credential in the credentials store.

        Args:
            data (dict): Collection data.

        Example:
            >>> pcce.credentials.add()
        """
        schema = CredentialSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post(json=validated_data)

    def delete(self, _id: str) -> None:
        """
        Deletes a credential from the credential store.

        Args:
            id (str): ID is the credential ID to delete.

        Example:
            >>> pcce.credentials.delete('aws-credential')
        """
        self._delete(f"{_id}")

    def get_usages(self, id: str) -> list[dict]:
        """
        Retrieves all usages for a specific credential in the credential store.

        Args:
            id (str): ID is the credential ID.

        Example:
            >>> pcce.credentials.get_usages('aws-credential')
        """
        return self._get(f"{id}/usages")
