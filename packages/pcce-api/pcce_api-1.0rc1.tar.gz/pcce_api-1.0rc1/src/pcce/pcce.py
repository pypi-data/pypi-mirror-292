"""
PCCE
"""

from __future__ import annotations

import base64
import os
import warnings

from restfly import APISession
from restfly.utils import url_validator

from ._version import __version__
from .agentless import AgentlessAPI
from .application_control import ApplicationControllAPI
from .audits import AuditsAPI
from .authenticate import AuthenticateAPI
from .authenticate_client import AuthenticateClientAPI
from .certs import CertsAPI
from .cloud import CloudAPI
from .coderepos_ci import CodereposCIAPI
from .collections import CollectionsAPI
from .containers import ContainersAPI
from .credentials import CredentialsAPI
from .current import CurrentAPI
from .custom_compliance import CustomComplianceAPI
from .custom_rules import CustomRulesAPI
from .defenders import DefendersAPI
from .feeds import FeedsAPI
from .groups import GroupsAPI
from .hosts import HostsAPI
from .images import ImagesAPI
from .ping import PingAPI
from .policies import PoliciesAPI
from .profiles import ProfilesAPI
from .registry import RegistryAPI
from .sandbox import SandboxAPI
from .scans import ScansAPI
from .serverless import ServerlessAPI
from .settings import SettingsAPI
from .signup import SignupAPI
from .stats import StatsAPI
from .statuses import StatusesAPI
from .tags import TagsAPI
from .tas_droplets import TASDropletsAPI
from .trust import TrustAPI
from .users import UsersAPI
from .util import UtilAPI
from .version import VersionAPI
from .vms import VMsAPI
from .waas import WAASAPI


class PCCE(APISession):
    """PCCE"""

    _lib_name = "pcce"
    _lib_version = __version__
    _backoff = 1
    _retries = 3
    _auth_mech = None
    _ssl_verify = False
    _conv_json = True

    def __init__(self, **kwargs):
        self._url = kwargs.get("url", os.environ.get("PCCE_URL", self._url))
        if not url_validator(self._url):
            raise TypeError(f"{self._url} is not a valid URL")
        super().__init__(**kwargs)

    def _basic_auth(self, username, password):
        credentials = f"{username}:{password}"
        credentials_bytes = credentials.encode("utf-8")
        encode_bytes = base64.b64encode(credentials_bytes)
        encode_credentials = encode_bytes.decode("utf-8")
        self._session.headers.update({"Authorization": f"Basic {encode_credentials}"})

    def _token_auth(self, username, password):
        token = self.post("api/v1/authenticate", json={"username": username, "password": password}).get("token")
        self._session.headers.update({"Authorization": f"Bearer {token}"})

    def _client_cert_auth(self, cert):
        token = self.post("api/v1/authenticate-client", cert=cert).get("token")
        self._session.headers.update({"Authrization": f"Bearer {token}"})

    def _authenticate(self, **kwargs):
        """
        This method handles authentication for token, basic and client certificate
        authentication.
        """
        self._auth_dict = kwargs.get(
            "_auth_dict",
            {
                "username": kwargs.get("username", os.getenv("PCCE_USERNAME")),
                "password": kwargs.get("password", os.getenv("PCCE_PASSWORD")),
            },
        )
        self._client_cert_auth_dict = kwargs.get(
            "_client_cert_auth_dict", {"cert": kwargs.get("cert_path", os.getenv("PCCE_CERT_PATH"))}
        )
        if None not in [v for _, v in self._client_cert_auth_dict.items()]:
            self._client_cert_auth(**self._client_cert_auth_dict)
        elif None not in [v for _, v in self._auth_dict.items()]:
            self._token_auth(**self._auth_dict)
        else:
            warnings.warn("Starting an unauthenticated session", stacklevel=2)
            self._log.warning("Starting an unauthenticated session.")

    @property
    def agentless(self):
        """
        The interface object for the PCCE Agentless APIs.
        """
        return AgentlessAPI(self)

    @property
    def application_control(self):
        """
        The interface object for the PCCE Application Control APIs.
        """
        return ApplicationControllAPI(self)

    @property
    def audits(self):
        """
        The interface object for the PCCE Audits APIs.
        """
        return AuditsAPI(self)

    @property
    def authenticate_client(self):
        """
        The interface object for the PCCE Authenticate Client APIs.
        """
        return AuthenticateClientAPI(self)

    @property
    def authenticate(self):
        """
        The interface object for the PCCE Authenticate APIs.
        """
        return AuthenticateAPI(self)

    @property
    def certs(self):
        """
        The interface object for the PCCE Certs APIs.
        """
        return CertsAPI(self)

    @property
    def cloud(self):
        """
        The interface object for the PCCE Cloud APIs.
        """
        return CloudAPI(self)

    @property
    def coderepos_ci(self):
        """
        The interface object for the PCCE Coderepo CI APIs.
        """
        return CodereposCIAPI(self)

    @property
    def collections(self):
        """
        The interface object for the PCCE Collections APIs.
        """
        return CollectionsAPI(self)

    @property
    def containers(self):
        """
        The interface object for the PCCE Containers APIs.
        """
        return ContainersAPI(self)

    @property
    def credentials(self):
        """
        The interface object for the PCCE Credentials APIs.
        """
        return CredentialsAPI(self)

    @property
    def current(self):
        """
        The interface object for the PCCE Current APIs.
        """
        return CurrentAPI(self)

    @property
    def custom_compliance(self):
        """
        The interface object for the PCCE Custom Compliance APIs.
        """
        return CustomComplianceAPI(self)

    @property
    def custom_rules(self):
        """
        The interface object for the PCCE Custom Rules APIs.
        """
        return CustomRulesAPI(self)

    @property
    def defenders(self):
        """
        The interface object for the PCCE Defenders APIs.
        """
        return DefendersAPI(self)

    @property
    def feeds(self):
        """
        The interface object for the PCCE Feeds APIs.
        """
        return FeedsAPI(self)

    @property
    def groups(self):
        """
        The interface object for the PCCE Groups APIs.
        """
        return GroupsAPI(self)

    @property
    def hosts(self):
        """
        The interface object for the PCCE Hosts APIs.
        """
        return HostsAPI(self)

    @property
    def images(self):
        """
        The interface object for the PCCE Images APIs.
        """
        return ImagesAPI(self)

    @property
    def ping(self):
        """
        The interface object for the PCCE _Ping APIs.
        """
        return PingAPI(self)

    @property
    def policies(self):
        """
        The interface object for the PCCE Policies APIs.
        """
        return PoliciesAPI(self)

    @property
    def profiles(self):
        """
        The interface object for the PCCE Profiles APIs.
        """
        return ProfilesAPI(self)

    @property
    def registry(self):
        """
        The interface object for the PCCE Registry APIs.
        """
        return RegistryAPI(self)

    @property
    def sandbox(self):
        """
        The interface object for the PCCE Sandbox APIs.
        """
        return SandboxAPI(self)

    @property
    def scans(self):
        """
        The interface object for the PCCE Scans APIs.
        """
        return ScansAPI(self)

    @property
    def serverless(self):
        """
        The interface object for the PCCE Serverless APIs.
        """
        return ServerlessAPI(self)

    @property
    def settings(self):
        """
        The interface object for the PCCE Settings APIs.
        """
        return SettingsAPI(self)

    @property
    def signup(self):
        """
        The interface object for the PCCE Signup APIs.
        """
        return SignupAPI(self)

    @property
    def stats(self):
        """
        The interface object for the PCCE Stats APIs.
        """
        return StatsAPI(self)

    @property
    def statuses(self):
        """
        The interface object for the PCCE Statuses APIs.
        """
        return StatusesAPI(self)

    @property
    def tags(self):
        """
        The interface object for the PCCE Tags APIs.
        """
        return TagsAPI(self)

    @property
    def tas_droplets(self):
        """
        The interface object for the PCCE TAS Droplets APIs.
        """
        return TASDropletsAPI(self)

    @property
    def trust(self):
        """
        The interface object for the PCCE Trust APIs.
        """
        return TrustAPI(self)

    @property
    def users(self):
        """
        The interface object for the PCCE Users APIs.
        """
        return UsersAPI(self)

    @property
    def util(self):
        """
        The interface object for the PCCE Util APIs.
        """
        return UtilAPI(self)

    @property
    def version(self):
        """
        The interface object for the PCCE Version APIs.
        """
        return VersionAPI(self)

    @property
    def vms(self):
        """
        The interface object for the PCCE VMs APIs.
        """
        return VMsAPI(self)

    @property
    def waas(self):
        """
        The interface object for the PCCE Waas APIs.
        """
        return WAASAPI(self)
