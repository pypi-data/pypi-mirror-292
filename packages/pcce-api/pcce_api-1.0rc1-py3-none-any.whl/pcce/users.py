"""
Users
"""

from __future__ import annotations

from restfly import APIEndpoint

from .schema.users import UserSchema


class UsersAPI(APIEndpoint):
    """Users"""

    _path = "api/v1/users"

    def list(self) -> list[dict]:
        """
        Retrieves a list of all users.
        """
        return self._get()

    def create(self, data: dict) -> None:
        """
        Adds a new user to the system.

        Args:
            data (dict): User data.
        """
        schema = UserSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        self._post(json=validated_data)

    def update(self, data: dict) -> None:
        """
        Updates an existing user in the system.

        Args:
            data (dict): User data.
        """
        schema = UserSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_data = schema.dump(schema.load(data))
        return self._put(json=validated_data)

    def update_password(self, old_password: str, new_password: str) -> None:
        """
        Changes the password of a user.
        """
        self._put("password", json={"oldPassword": old_password, "newPassword": new_password})

    def delete(self, username: str) -> None:
        """
        Deletes a user from the system.
        """
        self._delete(f"{username}")
