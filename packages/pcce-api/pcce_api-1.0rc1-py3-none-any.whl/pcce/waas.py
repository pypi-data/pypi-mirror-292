"""
WAAS
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint


class WAASAPI(APIEndpoint):
    """WAAS"""

    _path = "api/v1/waas"

    def scan(self, fobj: BytesIO) -> dict:
        """
        Scans the OpenAPI specifications file of size not more than 100 KB and generates a report for any errors, or
            shortcomings such as structural issues, compromised security, best practices, and so on. API definition
            scan supports scanning OpenAPI 2.X and 3.X definition files in either YAML or JSON formats.
        """
        return self._post("openapi-scans", data={"source": "manual"}, files={"spec": fobj})
