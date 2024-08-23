"""
Serverless
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.serverless import ServerlessParamsSchema
from .utils.file import download


class ServerlessAPI(APIEndpoint):
    """Serverless"""

    _path = "api/v1/serverless"

    def list(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all scan reports for the serverless functions which Prisma Cloud has been configured to scan.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ServerlessParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def download(self, params: dict | None = None) -> BytesIO:
        """
        Downloads all serverless scan reports in CSV format.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ServerlessParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("download", params=validated_params, stream=True)
        return download(response=resp)

    def resolve(self, data: dict) -> None:
        """
        Adds vulnerability data for the given functions

        Args:
            data (dict): Serverless function data.
        """
        self._post("evaluate", json=data)

    def names(self, params: dict | None = None) -> list[str]:
        """
        Retrieves all list of serverless function names which Prisma Cloud has been configured to scan.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ServerlessParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("names", params=validated_params)

    def scan(self) -> None:
        """
        Re-scan all serverless functions immediately.
        """
        self._post("scan")

    def stop(self) -> None:
        """
        Stops the ongoing serverless scan.
        """
        self._post("stop")
