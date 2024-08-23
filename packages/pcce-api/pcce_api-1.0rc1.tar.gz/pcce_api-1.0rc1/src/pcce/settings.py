"""
Settings
"""

from __future__ import annotations

from restfly import APIEndpoint
from restfly.utils import dict_clean

from .schema.settings import VMImageSettingsSchema


class SettingsAPI(APIEndpoint):
    """Settings"""

    _path = "api/v1/settings"

    def add_cert_client(self, access_ca_cert: str | None = None, certificate_period_days: int | None = None) -> None:
        """
        Sets a certificate authority (CA) to trust and the validity period for client certificates.

        Args:
            access_ca_cert (str): a custom CA certificate.
            certificate_period_days (int): the certificates period in days.
        """
        self._post(
            "certificates",
            json=dict_clean({"accessCaCert": access_ca_cert, "certificatePeriodDays": certificate_period_days}),
        )

    def get_cert(self) -> list[dict]:
        """
        Returns the Subject Alternative Name(s) (SANs) in Console's certificate.
        Defenders use these names to connect to Console.
        """
        return self._get("certs")

    def add_cert(self, console_san: list[str], ca_expiration: str, defender_old_expiration: str) -> None:
        """
        Adds or deletes Subject Alternative Name(s) (SANs) in Prisma Cloud Compute's certificate.

        Args:

        """
        self._post("certs")

    def list_code_repo(self) -> list[dict]:
        """
        Retrieves the list of code repositories Prisma Cloud is configured to scan.
        It also retrieves a partial webhook URL.
        """
        return self._get("coderepo")

    def update_code_repo(self) -> None:
        """
        Updates the code repositories to scan.
        """
        self._post("coderepo")

    def set_cert_console(self) -> None:
        """
        Sets the console certificate settings
        """
        self._post("console-certificate")

    def list_alert(self) -> list[dict]:
        """
        Returns the list of alert labels configured in Prisma Cloud Compute.
        """
        return self._get("custom-labels")

    def add_alert(self) -> None:
        """
        Creates a custom alert label to augment audit events.
        """
        self._post("custom-labels")

    def get_advanced_defender(self) -> dict:
        """
        Returns the advanced settings for Defenders.
        """
        return self._get("defender")

    def get_intelligence_stream(self) -> dict:
        """
        Returns the details about the Intelligence Stream configuration.
        """
        return self._get("intelligence")

    def add_intelligence_stream(self) -> None:
        """
        Configures the Intelligence Stream.
        """
        self._post("intelligence")

    def get_ldap_integration(self) -> dict:
        """
        Returns the LDAP integration settings.
        """
        return self._get("ldap")

    def add_ldap_integration(self) -> None:
        """
        Configures the LDAP integration.
        """
        self._post("ldap")

    def get_licence(self) -> dict:
        """
        Returns the details about the installed license.
        """
        return self._get("license")

    def add_license(self) -> None:
        """
        Configures the Prisma Cloud Compute license.
        """
        self._post("license")

    def get_logging(self) -> dict:
        """
        Returns the logging settings.
        """
        return self._get("logging")

    def add_logging(self) -> None:
        """
        Configures the logging settings.
        """
        self._post("logging")

    def get_logon(self) -> dict:
        """
        LogonSettings are settings associated with the login properties
        """
        return self._get("logon")

    def add_logon(self) -> None:
        """
        Configures the timeout for Prisma Cloud Compute sessions.
        """
        self._post("logon")

    def get_oauth(self) -> dict:
        """
        Returns the OAuth configuration settings.
        """
        return self._get("oauth")

    def add_oauth(self) -> None:
        """
        Configures the OAuth settings.
        """
        self._post("oauth")

    def get_openid(self) -> dict:
        """
        Returns the OpenID Connect configuration settings.
        """
        return self._get("oidc")

    def add_openid(self) -> None:
        """
        Configures the OpenID Connect settings.
        """
        self._post("oidc")

    def get_proxy(self) -> dict:
        """
        Returns the proxy settings for Prisma Cloud Compute containers to access the Internet.
        """
        return self._get("proxy")

    def add_proxy(self) -> None:
        """
        Configures the proxy settings.
        """
        self._post("proxy")

    def get_registry(self) -> dict:
        """
        Retrieves the list of registries Prisma Cloud is configured to scan.
        """
        return self._get("registry")

    def add_registry(self) -> None:
        """
        Specifies a single registry to scan.
        """
        self._post("registry")

    def update_registry(self) -> None:
        """
        Updates the registries to scan.
        """
        self._put("registry")

    def get_saml(self) -> dict:
        """
        Returns the configured SAML settings that is used to authenticate to the Prisma Cloud Compute console.
        """
        return self._get("saml")

    def add_saml(self) -> None:
        """
        Configures the SAML settings that is used to authenticate to the Prisma Cloud Compute.
        """
        self._post("saml")

    def get_scan(self) -> dict:
        """
        Returns the global settings for image, host, container, and registry scanning.
        """
        return self._get("scan")

    def add_scan(self) -> None:
        """
        Configures the Prisma Cloud Compute scanner settings.
        """
        self._post("scan")

    def get_tas(self) -> dict:
        """
        Retrieves Tanzu Application Service (TAS) settings.
        """
        return self._get("tas")

    def add_tas(self) -> None:
        """
        Sets the Tanzu Application Service (TAS) settings.
        """
        self._post("tas")

    def get_telemetry(self) -> dict:
        """
        Returns the telemetry settings that anonymously reports the threats and vulnerabilities to Prisma Cloud Compute.
        """
        return self._get("telemetry")

    def set_telemetry(self, enabled: bool) -> None:
        """
        Enables or disables the telemetry feature.

        Args:
            enabled (bool): determines whether the telemetry settings are enabled.
        """
        self._post("telemetry", json={"enableed": enabled})

    def get_vm_image(self) -> dict:
        """
        Retrieves the list of VM image scan scopes.
        """
        return self._get("vm")

    def update_vm_image(self, data: list) -> None:
        """
        Updates the list of VM image scan scopes.

        Args:
            data (list): VM Images settings data.
        """
        schema = VMImageSettingsSchema()
        errors = schema.validate(data, many=True)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_data = schema.dump(schema.load(data, many=True), many=True)
        self._put("vm", json=validated_data)

    def get_wildfire(self) -> dict:
        """
        Returns the wildfire settings
        """
        return self._get("wildfire")
