"""
Scans
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.scans import CIImageScansParamsSchema, ScansSchema
from .utils.file import download


class ScansAPI(APIEndpoint):
    """Scans"""

    _path = "api/v1/scans"

    def list_ci_image_result(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all scan reports for images scanned by the Jenkins plugin or twistcli.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = CIImageScansParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def get_ci_image_result(self, _id: str) -> dict:
        """
        Retrieves all scan reports for images scanned by the Jenkins plugin or twistcli tool for a specific image with
            an given id.
        """
        return self._get(f"{_id}")

    def add_cli_result(self, data: dict) -> None:
        """
        AddCLIScanResult adds a CLI scan result

        Args:
            data (dict): CLI Scan result data.
        """
        schema = ScansSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post(json=validated_data)

    def download_ci_image_result(self, params: dict | None = None) -> BytesIO:
        """
        Downloads all scan reports from the Jenkins plugin and twistcli in CSV format.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = CIImageScansParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("download", params=validated_params, stream=True)
        return download(response=resp)
