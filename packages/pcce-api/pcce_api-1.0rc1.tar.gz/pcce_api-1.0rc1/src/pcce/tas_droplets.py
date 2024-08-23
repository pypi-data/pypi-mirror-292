"""
TAS Droplets
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.tas_droplets import (ProgressTASDropletsParamsSchema,
                                  TASDropletsParamsSchema)
from .utils.file import download


class TASDropletsAPI(APIEndpoint):
    """TAS Droplets"""

    _path = "api/v1/tas-droplets"

    def list(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves scan reports for Tanzu Application Service (TAS) droplets.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = TASDropletsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def addresses(self, params: dict | None = None) -> list[dict]:
        """
        Gets the Cloud Controller Addresses of scanned Tanzu Application Service (TAS) droplets.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = TASDropletsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("addresses", params=validated_params)

    def download(self, params: dict | None = None) -> BytesIO:
        """
        Downloads scan reports for Tanzu Application Service (TAS) droplets in CSV format.

        Args:
            params (dict): Query parameters
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = TASDropletsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("download", params=validated_params, stream=True)
        return download(response=resp)

    def progress(self, params: dict | None = None) -> list[dict]:
        """
        Returns the details of the TAS Droplets ongoing scan.

        Args:
            params (dict): Query parameters
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ProgressTASDropletsParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("progress", params=validated_params)

    def scan(self) -> None:
        """
        Scans the TAS Droplets.
        """
        self._post("scan")

    def stop(self) -> None:
        """
        Stops the ongoing scan of TAS Droplets.
        """
        self._post("stop")
