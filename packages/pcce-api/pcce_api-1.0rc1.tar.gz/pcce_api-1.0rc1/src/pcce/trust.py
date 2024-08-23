"""
Trust
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.trust import TrustSchema


class TrustAPI(APIEndpoint):
    """Trust"""

    _path = "api/v1/trust/data"

    def get(self) -> dict:
        """
        Returns the trusted registries, repositories, and images.
        """
        return self._get()

    def update(self, data: dict) -> None:
        """
        Updates a trusted image to the system. Specify trusted images using either the image name or layers properties.

        Args:
            data (dict): Trust data.
        """
        schema = TrustSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._put(json=validated_data)
