"""
Sign up
"""

from __future__ import annotations

from restfly import APIEndpoint


class SignupAPI(APIEndpoint):
    """Sign up"""

    _path = "api/v1/signup"

    def create_admin_account(self, username: str, password: str) -> None:
        """
        Creates the initial admin user after Console is first installed.

        Args:
            username (str): the username used for authentication.
            password (str): the password used for authentication.
        """
        self._post(json={"username": username, "password": password})
