"""
Sandbox
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.sandbox import SandboxSchema


class SandboxAPI(APIEndpoint):
    """Sandbox"""

    _path = "api/v1/sandbox"

    def add(self, data: dict) -> dict:
        """
        Adds a sandbox scan result, the scan is augmented with geolocation data and returned to the client

        Args:
            data (dict): Sandbox data.
        """
        schema = SandboxSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        return self._post(json=validated_data)
