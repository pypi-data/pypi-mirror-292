"""
Custom Rules
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.custom_rules import CustomRuleSchema


class CustomRulesAPI(APIEndpoint):
    """Custom Rules"""

    _path = "api/v1/custom-rules"

    def list(self) -> list[dict]:
        """
        Retrieves a list of all custom rules.

        Example:
            >>> pcce.custom_rules.list()
        """
        return self._get()

    def delete(self, _id: str) -> None:
        """
        Deletes a custom rule.

        Example:
            >>> pcce.custom_rules.delete(10000)
        """
        self._delete(f"{_id}")

    def update(self, data: dict) -> None:
        """
        Creates/edits a custom rule.

        Args:
            data (dict): Custom Rules data.

        Example:
            >>> pcce.custom_rules.update()
        """
        schema = CustomRuleSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._put(f"{validated_data["_id"]}", json=validated_data)
