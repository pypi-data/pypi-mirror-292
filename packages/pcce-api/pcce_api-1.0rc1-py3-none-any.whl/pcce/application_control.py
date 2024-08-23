"""
Application Control
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.application_control import HostApplicationControlRuleSchema


class ApplicationControllAPI(APIEndpoint):
    """Application Control"""

    _path = "api/v1/application-control"

    def list(self) -> list[dict]:
        """
        Returns the host application control rules.

        Example:
            >>> pcce.application_control.list()
        """
        return self._get("host")

    def upsert(self, rule_data: dict) -> dict:
        """
        Upserts the host application control rule to the db and returns the upserted rule.

        Args:
            rule_data (dict):

        Example:
            >>> pcce.application_control.upsert({
                    "_id": 0,
                    "applications": [
                        {
                        "allowedVersions": [
                            "string",
                        ],
                        "name": "string"
                        }
                    ],
                    "description": "string",
                    "disabled": true,
                    "modified": "2024-07-03T15:11:19.250Z",
                    "name": "string",
                    "notes": "string",
                    "owner": "string",
                    "previousName": "string",
                    "severity": "string"
                })
        """
        schema = HostApplicationControlRuleSchema()
        valided_data = schema.dump(schema.load(rule_data))
        return self._put("host", json=valided_data)

    def delete(self, id: int) -> None:
        """
        Removes the given rule from the list of host application control rules.

        Args:
            id (str): Rule id to delete.

        Example:
            >>> pcce.
        """
        self._delete(f"host/{id}")
