"""
Hosts
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.hosts import HostScanResultsParamsSchema
from .utils.file import download


class HostsAPI(APIEndpoint):
    """Hosts"""

    _path = "api/v1/hosts"

    def list_scan_results(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all host scan reports.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.hosts.list_scan_results()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = HostScanResultsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def download_scan_results(self, params: dict | None = None) -> BytesIO:
        """
        Downloads all host scan reports in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.hosts.download_scan_results()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = HostScanResultsParamsSchema()
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

    def resolve_host(self) -> None:
        # TODO Create github issues
        """
        Adds vulnerability data for the given host

        Args:

        Example:
            >>> pcce.hosts.resolve_host()
        """
        self._post("evaluate")

    def get_host_info(self, params: dict | None = None) -> list[dict]:
        """
        Returns minimal information that includes hostname, distro, distro-release, collections, clusters, and
            agentless about all deployed hosts.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.hosts.get_host_info()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = HostScanResultsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("info", params=validated_params)

    def scan(self) -> None:
        """
        Re-scan all hosts immediately.

        Example:
            >>> pcce.hosts.scan()
        """
        return self._post("scan")
