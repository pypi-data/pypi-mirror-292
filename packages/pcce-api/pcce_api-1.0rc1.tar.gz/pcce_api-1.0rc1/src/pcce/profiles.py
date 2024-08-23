"""
Profiles
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.profiles import (AppEmbeddedProfileParamsSchema,
                              RuntimeProfileParamsSchema)
from .utils.file import download


class ProfilesAPI(APIEndpoint):
    """Profiles"""

    _path = "api/v1/profiles"

    def list_app_embedded(self, params: dict | None = None) -> list:
        """
        Retrieves the app-embedded observations.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = AppEmbeddedProfileParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("app-embedded", params=validated_params)

    def download_app_embedded(self, params: dict | None = None) -> BytesIO:
        """
        Downloads the app-embedded observations in a CSV format.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = AppEmbeddedProfileParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("app-embedded/download", params=validated_params, stream=True)
        return download(response=resp)

    def list_runtime_container(self, params: dict | None = None) -> list:
        """
        Retrieves the details and state of all runtime models.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeProfileParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("container", params=validated_params)

    def download_runtime_container(self, params: dict | None = None) -> BytesIO:
        """
        Retrieves the details and state of all runtime models in CSV format.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeProfileParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("container/download", params=validated_params, stream=True)
        return download(response=resp)

    def relearn_runtime_container(self) -> None:
        """
        Puts all containers into learning mode.
        """
        self._post("container/learn")

    def list_runtime_host(self, params: dict | None = None) -> list:
        """
        Retrieves the details and state of each host service runtime model on a host-by-host basis.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeProfileParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("host", params=validated_params)

    def download_runtime_host(self, params: dict | None = None) -> BytesIO:
        """
        Retrieves the details and state of each host service runtime model in CSV format.

        Args:
            params (dict): Query parameter.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeProfileParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("host/download", params=validated_params, stream=True)
        return download(response=resp)
