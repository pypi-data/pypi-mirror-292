"""
Containers
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.containers import ScanResultParamsSchema
from .utils.file import download


class ContainersAPI(APIEndpoint):
    """Containers"""

    _path = "api/v1/containers"

    # Monitor > Compliance > Containers
    def list_scan_result(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves container scan reports.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.containers.list_scan_result()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ScanResultParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def get_count(self, params: dict | None = None) -> int:
        """
        Returns an integer representing the number of containers in your environment.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.containers.get_count()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ScanResultParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("count", params=validated_params)

    def download_scan_result(self, params: dict | None = None) -> BytesIO:
        """
        Downloads container scan reports in CSV format.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.containers.download_scan_result()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ScanResultParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_name(self, params: dict | None = None) -> list[str]:
        """
        Returns an array of strings containing all container names.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.containers.list_name()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ScanResultParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("names", params=validated_params)

    def scan(self) -> None:
        """
        Re-scan all containers immediately.

        Example:
            >>> pcce.containers.scan()
        """
        self._post("scan")
