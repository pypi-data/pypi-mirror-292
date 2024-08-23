"""
Images
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint
from restfly.utils import dict_clean

from .schema.images import ImageParamsSchema
from .utils.file import download


class ImagesAPI(APIEndpoint):
    """Images"""

    _path = "api/v1/images"

    def list_scan_results(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves image scan reports.

        Args:
            params (dict): Query parameters.

        Example:
            pcce.images.list_scan_results()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ImageParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def download_scan_results(self, params: dict | None = None) -> BytesIO:
        """
        Downloads image scan reports in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            pcce.images.download_scan_results()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ImageParamsSchema()
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

    def resolve(self, images: dict) -> None:
        """
        Adds vulnerability data for the given images

        Args:
            images (dict): Images is the list of image to resolve.
        """
        # TODO schema for images
        return self._post("evaluate", json=images)

    def list_names(self, params: dict | None = None) -> list[str]:
        """
        Returns an array of strings containing image names.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.images.list_names()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ImageParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("names", params=validated_params)

    def scan(self, hostname: str | None = None, image_tag: dict | None = None) -> None:
        """
        Re-scan all images immediately. This endpoint returns the time that the scans were initiated.

        Args:
            hostname (str): Hostname is the optional host name to scan.
            image_tag (object): ImageTag represents an image repository and its associated tag or registry digest.

        Example:
            >>> pcce.images.scan()
        """
        return self._post("scan", json=dict_clean({"hostname": hostname, "imageTag": image_tag}))

    def download_app_embeded(self) -> BytesIO:
        """
        Generates the embedded defender bundle and serves it to the user.

        Example:
            >>> pcce.images.download_app_embeded()
        """
        resp = self._get("twistlock_defender_app_embedded.tar.gz", stream=True)
        return download(response=resp)

    def download_serverless(self) -> BytesIO:
        """
        Returns a ZIP file with a Lambda layer containing the Defender runtime.

        Example:
            >>> pcce.images.download_serverless()
        """
        resp = self._post("twistlock_defender_layer.zip", stream=True)
        return download(response=resp)
