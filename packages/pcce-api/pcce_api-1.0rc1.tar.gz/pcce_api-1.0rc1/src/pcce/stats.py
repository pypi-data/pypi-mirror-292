"""
Stats
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from pcce.utils.file import download

from .schema.stats import (ComplianceStatParamsSchema, EventStatParamsSchema,
                           VulnStatParamsSchema)


class StatsAPI(APIEndpoint):
    """Stats"""

    _path = "api/v1/stats"

    def get_app_firewall(self) -> int:
        """
        Returns the number of app firewalls in use
        """
        return self._get("app-firewall/count")

    def get_compliance(self, params: dict | None = None) -> dict:
        """
        Returns compliance statistics, including:

            - Compliance rate by regulation, CIS benchmark, and policy rule.
            - Trend of failed compliance checks over time.
            - List of all compliance checks with their corresponding compliance rate.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ComplianceStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("compliance", params=validated_params)

    def download_compliance(self, params: dict | None = None) -> BytesIO:
        """
        DownloadComplianceStats downloads the compliance stats

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ComplianceStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("compliance/download", params=validated_params, stream=True)
        return download(response=resp)

    def fresh_compliance(self, params: dict | None = None) -> dict:
        """
        Refreshes the current day's list and counts of compliance issues, as well as the list of affected running
            resources.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ComplianceStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._post("compliance/refresh", params=validated_params)

    def get_daily(self) -> list:
        """
        Returns a historical list of per-day statistics for the resources protected by Prisma Cloud Compute, including
            the total number of runtime audits, image vulnerabilities, and compliance violations.
        """
        return self._get("daily")

    def get_dashboard(self) -> dict:
        """
        Returns statistics about the resources protected by Prisma Cloud Compute, including the total number of runtime
            audits, image vulnerabilities, and compliance violations.
        """
        return self._get("dashboard")

    def get_event(self, params: dict | None = None) -> dict:
        """
        Returns events statistics for your environment.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = EventStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("events", params=validated_params)

    def get_license(self) -> dict:
        """
        returns the license stats including the credit per defender
        """
        return self._get("license")

    def get_vulnerability(self, params: dict | None = None) -> dict:
        """
        Returns a list of vulnerabilities (CVEs) in the deployed images, registry images, hosts, and serverless
            functions affecting your environment.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VulnStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("vulnerabilities", params=validated_params)

    def download_vulnerability(self, params: dict | None = None) -> BytesIO:
        """
        Downloads a list of vulnerabilities (CVEs) in the deployed images, registry images, hosts, and serverless
            functions affecting your environment in a CSV format.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VulnStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("vulnerabilities/download", params=validated_params, stream=True)
        return download(response=resp)

    def get_impacted_resource_vulnerability(self, params: dict | None = None) -> dict:
        """
        Generates a list of impacted resources for a specific vulnerability. This endpoint returns a list of all
            deployed images, registry images, hosts, and serverless functions affected by a given CVE.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VulnStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("vulnerabilities/impacted-resources", params=validated_params)

    def download_impacted_resource_vulnerability(self, params: dict | None = None) -> BytesIO:
        """
        Downloads a list of impacted resources for a specific vulnerability in a CSV format. This endpoint returns a
            list of all deployed images, registry images, hosts, and serverless functions affected by a given CVE.

        Args:
            params (dict): Query parameters.
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = VulnStatParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("vulnerabilities/impacted-resources/download", params=validated_params, stream=True)
        return download(response=resp)

    def fresh_vulnerability(self) -> dict:
        """
        Refreshes the current day's CVE counts and CVE list, as well as their descriptions.
        """
        return self._post("vulnerabilities/refresh")
