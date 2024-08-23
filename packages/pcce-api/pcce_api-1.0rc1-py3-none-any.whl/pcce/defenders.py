"""
Defenders
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint
from restfly.utils import dict_clean

from .schema.defenders import (AppEmbededDefenderSchema, DefendersParamsSchema,
                               DefendersSchema, FargateParamsSchema,
                               ServerlessDefenderSchema)
from .utils.file import download


class DefendersAPI(APIEndpoint):
    """Defenders"""

    _path = "api/v1/defenders"

    def list_deployed(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all deployed Defenders.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.defenders.list_deployed()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DefendersParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(params=validated_params)

    def generate_dockerfile_for_app_embedded(self, data: dict) -> BytesIO:
        """
        Creates an augmented Dockerfile with Defender and dependencies included as a ZIP file.

        Args:
            data (dict): App Embedded data.

        Example:
            >>> pcce.defenders.generate_dockerfile_for_app_embedded()
        """
        schema = AppEmbededDefenderSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        resp = self._post(
            "app-embedded",
            json=validated_data,
            stream=True,
        )
        return download(response=resp)

    def generate_daemon_set(self, data: dict) -> BytesIO:
        """
        Creates a DaemonSet deployment file in YAML format that you can use to deploy Defender to your cluster.

        Args:
            data (dict): DaemonSet deployment data.

        Example:
            >>> pcce.defenders.generate_daemon_set()
        """
        schema = DefendersSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        resp = self._post(
            "daemonset.yaml",
            json=validated_data,
            stream=True,
        )
        return download(response=resp)

    def download_deployed(self, params: dict | None = None) -> BytesIO:
        """
        Downloads information about deployed Defenders in CSV format. Use the query parameters to filter
            what data is returned.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.defenders.download_deployed()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DefendersParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def generate_protected_json_fargate(self, params: dict | None = None) -> BytesIO:
        """
        Returns a protected Fargate task definition given an unprotected task definition.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.defenders.generate_protected_json_fargate()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = FargateParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._post(
            "fargate.json",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def generate_protected_yaml_fargate(self, params: dict | None = None) -> BytesIO:
        """
        Returns a protected Fargate task definition for a CloudFormation YAML template given an unprotected task
            definition.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.defenders.generate_protected_yaml_fargate()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = FargateParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._post(
            "fargate.yaml",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def generate_helm_deployment(self, data: dict) -> BytesIO:
        """
        Creates a Helm deployment file that you can use to deploy Defenders to your cluster.

        Args:
            data (dict): Helm deployment data.

        Example:
            >>> pcce.defenders.generate_helm_deployment()
        """
        schema = DefendersSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        resp = self._post(
            "twistlock-defender-helm.tar.gz",
            json=validated_data,
            stream=True,
        )
        return download(response=resp)

    def get_image_name(self) -> str:
        """
        Returns the full Docker image name for Defender.

        Example:
            >>> pcce.defenders.get_image_name()
        """
        return self._get("image-name")

    def get_cert_bundle(self, params: dict | None = None) -> dict:
        """
        Returns the certificate bundle that Defender needs to securely connect to Console.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.defenders.get_cert_bundle()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = FargateParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("install-bundle", params=validated_params)

    def get_defender_name(self, params: dict | None = None) -> list[str]:
        """
        Retrieves a list of Defender hostnames

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.defenders.get_defender_name()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DefendersParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("names", params=validated_params)

    def generate_serverless(self, data: dict) -> BytesIO:
        """
        Downloads a ZIP file with serverless Defender bundle.

        Args:
            data (dict): Serverless deployment data.

        Example:
            >>> pcce.defenders.generate_serverless()
        """
        schema = ServerlessDefenderSchema()
        errors = schema.validate(data)
        if errors:
            raise ValueError(f"Invalid data: {errors}")
        validated_data = schema.dump(schema.load(data))
        resp = self._post(
            "serverless/bundle",
            json=validated_data,
            stream=True,
        )
        return download(response=resp)

    def list_summary(self) -> list[dict]:
        """
        Lists the number of Defenders in each defender category

        Example:
            >>> pcce.defenders.list_summary()
        """
        return self._get("summary")

    def upgrade_connected_linux(self, params: dict | None = None) -> None:
        """
        Upgrades all connected single Linux Container Defenders.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.defenders.upgrade_connected_linux()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DefendersParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        self._post("upgrade", params=validated_params)

    def delete(self, _id: str) -> None:
        """
        Deletes an existing Defender on a given host.

        Args:
            id (str): Hostname is a name of a specific Defender to delete.

        Example:
            >>> pcce.defenders.delete('string')
        """
        self._delete(f"{_id}")

    def update_configuration(
        self, _id: str, cluster_monitoring: bool | None = None, proxy_listener_type: str | None = None
    ) -> None:
        """
        Updates a deployed Defender's configuration.

        Args:
            id (str): Hostname is a name of a specific Defender to update.
            cluster_monitoring (bool): Indicates whether any of the cluster monitoring features are enabled (monitor
                service accounts, monitor Istio, collect Kubernetes pod labels).
            proxy_listener_type (str): ProxyListenerType is the proxy listener type of defenders.

        Example:
            >>> pcce.defenders.update_configuration('string', cluster_monitoring=True)
        """

        return self._post(
            f"{_id}/features",
            json=dict_clean({"clusterMonitoring": cluster_monitoring, "proxyListenerType": proxy_listener_type}),
        )

    def restart(self, _id: str) -> None:
        """
        Restarts Defender on a given host.

        Args:
            _id (str): Hostname is a name of a specific Defender to restart.

        Example:
            >>> pcce.defenders.restart('string')
        """
        return self._post(f"{_id}/restart")

    def upgrade(self, _id: str) -> None:
        """
        Upgrades Defender on <HOSTNAME>.

         Args:
            id (str): Hostname is a name of a specific Defender to upgrade.

        Example:
            >>> pcce.defenders.upgrade('string')
        """
        return self._post(f"{_id}/upgrade")
