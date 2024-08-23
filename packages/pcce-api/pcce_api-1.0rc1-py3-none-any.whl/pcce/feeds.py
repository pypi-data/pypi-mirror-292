"""
Feeds
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.feeds import MalwareSchema, VulsSchema


class FeedsAPI(APIEndpoint):
    """Feeds"""

    _path = "api/v1/feeds/custom"

    def get_custom_vuls(self) -> dict:
        """
        Returns the custom vulnerabilities feed.

        Example:
            >>> pcce.feeds.get_custom_vuls()
        """
        return self._get("custom-vulnerabilities")

    def set_custom_vuls(self, data: dict) -> None:
        """
        Sets the custom vulnerabilities feed

        Args:
            data (dict): Vulnerabilities data

        Example:
            >>> pcce.feeds.set_custom_vuls()
        """
        schema = VulsSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._put("custom-vulnerabilities", json=validated_data)

    def get_custom_malware(self) -> dict:
        """
        Returns the custom malware feed.

        Example:
            >>> pcce.feeds.get_custom_malware()
        """
        return self._get("malware")

    def set_custom_malware(self, data: dict) -> None:
        """
        Sets the custom malware feed.

        Args:
            data (dict): Malware data

        Example:
            >>> pcce.feeds.set_custom_malware()
        """
        schema = MalwareSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        return self._put("malware", json=validated_data)
