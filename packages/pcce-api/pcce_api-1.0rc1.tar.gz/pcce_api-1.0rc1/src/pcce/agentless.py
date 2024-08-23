"""
Agentless
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.agentless import AgentlessSchema
from .utils.file import download


class AgentlessAPI(APIEndpoint):
    """Agentless"""

    _path = "api/v1/agentless"

    def progress(self) -> list[dict]:
        """
        Shows the progress of an ongoing scan on hosts or containers for vulnerabilities and compliance.

        Example:
            >>> pcce.agentless.progress()
        """
        return self._get("progress")

    def scan(self) -> None:
        """
        Scans the hosts or containers for vulnerabilities and compliance.

        Example:
            >>> pcce.agentless.scan()
        """
        self._post("scan")

    def stop(self) -> None:
        """
        Stops an ongoing scan on hosts or containers for vulnerabilities and compliance.

        Example:
            >>> pcce.agentless.stop()
        """
        self._post("stop")

    def templates(self, data: dict) -> BytesIO:
        """
        Downloads a tarball file that contains the agentless resource permission templates for the cloud accounts.

        Args:
            data (dict): Agentless data

        Example:
            >>> pcce.agentless.template()
        """
        schema = AgentlessSchema()
        valided_data = schema.dump(schema.load(data))
        resp = self._post(
            "templates",
            json=valided_data,
            stream=True,
        )
        return download(response=resp)
