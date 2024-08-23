"""
Certs
"""

from __future__ import annotations

from restfly import APIEndpoint
from restfly.utils import dict_clean


class CertsAPI(APIEndpoint):
    """Certs"""

    _path = "api/v1/certs"

    def get_ca_pem(self) -> str:
        """
        Retrieves the Base64-encoded SSL root certificate self-signed by primary certificate authority (CA) in PEM
            format.

        Example:
            >>> pcce.certs.get_ca_pem()
        """
        return self._get("ca.pem")

    def get_server_cert(self, os: str | None = None, ip: str | None = None, hostname: str | None = None) -> str:
        """
        Retrieves the server certificate bundle from Prisma Cloud Compute that contains a chain of certificates.

            Certificate Authority (CA) certificate in PEM
            RSA Private Key for server in PEM
            Server certificate in PEM
            Defender CA certificate in PEM
            Defender RSA Private Key for client in PEM
            Defender client certificate in PEM

        Example:
            >>> pcce.certs.get_server_cert()
        """
        return self._get("server-cert.sh", params=dict_clean({"os": os, "ip": ip, "hostname": hostname}))
