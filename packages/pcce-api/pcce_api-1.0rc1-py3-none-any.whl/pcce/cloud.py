"""
Cloud
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.cloud import (DiscoveryEntitiesParamsSchema,
                           DiscoveryResultParamsSchema,
                           DiscoveryVMsParamsSchema)
from .utils.file import download


class CloudAPI(APIEndpoint):
    """Cloud"""

    _path = "api/v1/cloud"

    def list_discovery_result(self, params: dict | None = None) -> list:
        """
        Returns a list of all cloud discovery scan results in a paginated response.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.cloud.list_discovery_result()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DiscoveryResultParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "discovery",
            params=validated_params,
        )

    def download_discovery_result(self, params: dict | None = None) -> BytesIO:
        """
        Downloads all cloud scan data in a CSV file.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.cloud.download_discovery_result()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DiscoveryResultParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "discovery/download",
            params=validated_params,
        )
        return download(response=resp)

    def list_discovery_entities(self, params: dict | None = None) -> list:
        """
        Returns a list of discovered cloud entities.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.cloud.list_discovery_entities()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DiscoveryEntitiesParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "discovery/entities",
            params=validated_params,
        )

    def scan_discovery(self) -> None:
        """
        Initiates a new cloud discovery scan.

        Example:
            >>> pcce.cloud.scan_discovery()
        """
        self._post("scan")

    def stop_discovery(self) -> None:
        """
        Terminates a cloud discovery scan that's in progress.

        Example:
            >>> pcce.cloud.stop_discovery()
        """
        self._post("stop")

    def list_discovery_vms(self, params: dict | None = None) -> list:
        """
        Returns the discovered cloud VM instances.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.cloud.list_discovery_vms()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DiscoveryVMsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "vms",
            params=validated_params,
        )
