"""
Authenticate Client
"""

from __future__ import annotations

from restfly import APIEndpoint


class AuthenticateClientAPI(APIEndpoint):
    """Authenticate Client"""

    _path = "api/v1/authenticate-client"

    def get(self, cert_path: str) -> dict:
        """
        Retrieves an access token using a client certificate.

        Args:
            cert_path: must PEM format, include client certificate concatenated together with a private key.

        Return:
            token: Token is the Prisma JWT token used for authentication.

        Example:
            >>> token = pcce.authenticate-client.get()
        """
        return self._post(cert=cert_path)["token"]
