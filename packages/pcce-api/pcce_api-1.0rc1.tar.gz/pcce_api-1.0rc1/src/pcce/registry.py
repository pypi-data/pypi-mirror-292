"""
Registry
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.registry import (ProgressRegistryParamsSchema,
                              RegistryParamsSchema, ScanRegistrySchema,
                              WebhookRegistrySchema)
from .utils.file import download


class RegistryAPI(APIEndpoint):
    """Registry"""

    _path = "api/v1/registry"

    def list(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves registry image scan reports.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RegistryParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def download(self, params: dict | None = None) -> BytesIO:
        """
        Downloads registry image scan reports in CSV format.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RegistryParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("download", params=validated_params, stream=True)
        return download(response=resp)

    def list_name(self, params: dict | None = None) -> list:
        """
        Retrieves a list of image names from current scanned registry images.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RegistryParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("names", params=validated_params)

    def add_webhook(self, data: dict) -> None:
        """
        RegistryWebhook listen to registry updates

        Args:
            data (dict): Registry Webhook data.
        """
        schema = WebhookRegistrySchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post("webhook/webhook", json=validated_data)

    def remove_webhook(self) -> None:
        """
        RegistryWebhook listen to registry updates
        """
        self._delete("webhook/webhook")

    def progress(self, params: dict | None = None) -> list[dict]:
        """
        Shows the progress of an ongoing regular or on-demand registry scan. By default, the API endpoint displays the
        progress of a regular scan.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ProgressRegistryParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("progress", params=validated_params)

    def scan(self, data: dict) -> None:
        """
        Triggers a new scan for all images when a new image is added to the registry or a new scan for an individual
        image.

        Args:
            data (dict): Scan data.
        """
        schema = ScanRegistrySchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post("scan", json=validated_data)

    def scan_registries(self, data: dict) -> None:
        """
        Sends a registry scan request to all registry scanner defenders

        Args:
            data (dict): Scan data.
        """
        schema = ScanRegistrySchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post("scan/select", json=validated_data)

    def stop(self) -> None:
        """
        Stops current registry scan immediately.
        """
        self._post("stop")
