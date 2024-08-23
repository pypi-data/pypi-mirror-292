"""
Authenticate
"""

from __future__ import annotations

from restfly import APIEndpoint


class AuthenticateAPI(APIEndpoint):
    """Authenticate"""

    _path = "api/v1/authenticate"

    def get(self, username: str, password: str) -> str:
        """
        Retrieves an access token using your username and password.

        Args:
            password (str): Password is the password used for authentication.
            username (str): Username is the username used for authentication.

        Return:
            token (str): Token is the Prisma JWT token used for authentication.

        Example:
            >>> pcce.authenticate.get(username='test', password='test')
        """
        return self._post(json={"username": username, "password": password})["token"]
