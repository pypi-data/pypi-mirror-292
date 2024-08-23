"""
VMs
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from pcce.utils.file import download

from .schema.vms import VMImagesParamsSchema


class VMsAPI(APIEndpoint):
    """VMs"""

    _path = "api/v1/vms"

    def list(self, params: dict | None = None) -> list[dict]:
        """
        Returns all VM image scan reports.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.vms.list()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VMImagesParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def download(self, params: dict | None = None) -> BytesIO:
        """
        Returns all VM image scan reports in CSV format.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VMImagesParamsSchema()
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

    def tags(self, params: dict | None = None) -> list[dict]:
        """
        Returns an array of strings containing all AWS tags of the scanned VM images.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VMImagesParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("labels", params=validated_params)

    def names(self, params: dict | None = None) -> list[dict]:
        """
        Returns an array of strings containing VM image names.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VMImagesParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("names", params=validated_params)

    def scan(self) -> None:
        """
        Re-scans all VM images immediately. This endpoint returns the time that the scans were initiated.
        """
        self._post("scan")

    def stop(self) -> None:
        """
        Stops the current VM image scan.
        """
        self._post("stop")
