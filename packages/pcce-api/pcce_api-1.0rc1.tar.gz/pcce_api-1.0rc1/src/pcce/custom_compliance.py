"""
Custom Compliance
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.custom_compliance import CustomComplianceSchema


class CustomComplianceAPI(APIEndpoint):
    """Custom Compliance"""

    _path = "api/v1/custom-compliance"

    def list(self) -> list[dict]:
        """
        Returns a list of all custom compliance checks.

        Example:
            >>> pcce.custom_compliance.list()
        """
        return self._get()

    def update(self, data: dict) -> dict:
        """
        Updates of the custom compliance checks.

        Args:
            data (dict): Custom Compliance data.

        Example:
            >>> pcce.custom_compliance.update()
        """
        schema = CustomComplianceSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        return self._put(json=validated_data)

    def delete(self, id: str):
        """
        Deletes a specific custom compliance checks.

        Args:
            _id (int): ID is the compliance check ID.

        Example:
            >>> pcce.custom_compliance.delete(10000)
        """
        self._delete(f"{id}")
