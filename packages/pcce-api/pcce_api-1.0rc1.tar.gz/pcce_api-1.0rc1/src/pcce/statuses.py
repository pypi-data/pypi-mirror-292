"""
Statuses
"""

from __future__ import annotations

from restfly import APIEndpoint


class StatusesAPI(APIEndpoint):
    """Statuses"""

    _path = "api/v1/statuses"

    def get_registry_scan(self) -> dict:
        """
        Returns the status of a regular registry scan that might include the following information:

            - Scan is completed: "completed": true
            - Scan is ongoing.
            - Errors: 10 most recent aggregated errors that occurred during the scan with error messages such as:
                - "Failed to retrieve repositories info..."
                - "Failed to query image details..."
                - "No available Defender was found"
        """
        return self._get("registry")
