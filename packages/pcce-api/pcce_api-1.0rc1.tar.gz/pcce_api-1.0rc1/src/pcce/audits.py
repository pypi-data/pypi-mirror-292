"""
Audits
"""

from __future__ import annotations

from io import BytesIO

from restfly import APIEndpoint

from .schema.audits import (AdmissionParamsSchema, CNNSContainerParamsSchema,
                            CNNSHostParamsSchema, DockerAccessParamsSchema,
                            IncidentParamsSchema, KubernetesParamsSchema,
                            ManagementParamsSchema,
                            RuntimeFileIntegrityParamsSchema,
                            RuntimeLogInspectionParamsSchema,
                            RuntimeParamsSchema, RuntimeServerlessParamsSchema,
                            RuntimeServerlessTimeframeParamsSchema,
                            RuntimeTimeframeParamsSchema, TrustParamsSchema,
                            WAASParamsSchema, WAASTimeframeParamsSchema)
from .utils.file import download


class AuditsAPI(APIEndpoint):
    """Audits"""

    _path = "api/v1/audits"

    # Monitor > Events > Docker audits
    def list_docker_access(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all docker access audit events that are logged and aggregated for any container resource protected by
        a Defender in Prisma Cloud Compute.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_docker_access()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DockerAccessParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dumps(schema.load(params))
        return self._get("access", params=validated_params)

    def download_docker_access(self, params: dict | None = None) -> BytesIO:
        """
        Returns the docker access audit events data in CSV format that are logged and aggregated for any container
        resource protected by a Defender in Prisma Cloud Compute.

         Args:
            params (dict): Query parameters

        Example:
            >>> pcce.audits.download_docker_access()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = DockerAccessParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "access/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    # Monitor > Events > Admission audits
    def list_admission(self, params: dict | None = None) -> list[dict]:
        """
        Returns all activities that were alerted or blocked by Defender functioning as Open Policy Agent admission
        controller.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.audits.list_admission()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = AdmissionParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("admission", params=validated_params)

    def download_admission(self, params: dict | None = None) -> BytesIO:
        """
        Returns the access admission events data in CSV format that were alerted or blocked by Defender functioning as
        Open Policy Agent admission controller.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.audits.download_admission()
        """
        if params is None:
            params = {}
        schema = AdmissionParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "admission/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_waas_agentless(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all agentless Web-Application and API Security (WAAS) audit events.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.audits.list_waas_agentless()
        """
        if params is None:
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("firewall/app/agentless", params=validated_params)

    def download_waas_agentless(self, params: dict | None = None) -> BytesIO:
        """
        Returns the agentless Web-Application and API Security (WAAS) audit events data in CSV format.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.audits.download_waas_agentless()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "firewall/app/agentless/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_waas_agentless_timeframe(self, params: dict | None = None) -> dict:
        """
        Retrieves all agentless Web-Application and API Security (WAAS) audit buckets based on a specified query time
        frame.

        Args:
            params (dict): Query parameters

        Example:
            >>> pcce.audits.get_waas_agentless_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/agentless/timeslice",
            params=validated_params,
        )

    def list_waas_app_embedded(self, params: dict | None = None) -> list[dict]:
        """
        Returns all app-embedded WAAS audit events for the specified query parameters.

        Args:
            params (dict): Query parameters.
        Example:
            >>> pcce.audits.list_waas_app_embedded()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get("firewall/app/app-embedded", params=validated_params)

    def download_waas_app_embedded(self, params: dict | None = None) -> BytesIO:
        """
        Returns the app-embedded WAAS audit events data in CSV format for the specified query parameters.

        Args:
            params (dict): Query parameters.
        Example:
            >>> pcce.audits.download_waas_app_embedded()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "firewall/app/app-embedded/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_waas_app_embedded_timeframe(self, params: dict | None = None) -> dict:
        """
        Returns the app-embedded WAAS audit buckets based on the query time frame. Use the UTC time of an audit event
        to query for a time frame.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_waas_app_embedded_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/app-embedded/timeslice",
            params=validated_params,
        )

    def list_waas_container(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all container Web-Application and API Security (WAAS) audits

        Args:
            params (dict): Query parameters.
        Example:
            >>> pcce.audits.list_waas_container()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/container",
            params=validated_params,
        )

    def download_waas_container(self, params: dict | None = None) -> BytesIO:
        """
        Returns the container Web-Application and API Security (WAAS) audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_waas_container()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "firewall/app/container/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_waas_container_timeframe(self, params: dict | None = None) -> dict:
        """
        Returns container firewall audit buckets according to the query timeframe

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_waas_container_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/container/timeslice",
            params=validated_params,
        )

    def list_waas_host(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all host Web-Application and API Security (WAAS) audit events.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_waas_host()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/host",
            params=validated_params,
        )

    def download_waas_host(self, params: dict | None = None) -> BytesIO:
        """
        Returns the host Web-Application and API Security (WAAS) audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_waas_host()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "firewall/app/host/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_waas_host_timeframe(self, params: dict | None = None) -> dict:
        """
        Returns host firewall audit buckets according to the query timeframe.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_waas_host_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/host/timeslice",
            params=validated_params,
        )

    def list_waas_serverless(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all serverless function Web-Application and API Security (WAAS) audit events.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_waas_serverless()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/serverless",
            params=validated_params,
        )

    def download_waas_serverless(self, params: dict | None = None) -> BytesIO:
        """
        Returns the serverless function Web-Application and API Security (WAAS) audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_waas_serverless()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "firewall/app/serverless/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_waas_serverless_timeframe(self, params: dict | None = None) -> dict:
        """
        Retrieves all serverless Web-Application and API Security (WAAS) audit buckets based on a specified query time
            frame in UTC.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_waas_serverless_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = WAASTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/app/serverless/timeslice",
            params=validated_params,
        )

    def list_cnns_container(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all Cloud Native Network Segmentation (CNNS) container audit events.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_cnns_container()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = CNNSContainerParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/network/container",
            params=validated_params,
        )

    def download_cnns_container(self, params: dict | None = None) -> BytesIO:
        """
        Returns the Cloud Native Network Segmentation (CNNS) container audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_cnns_container()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = CNNSContainerParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "firewall/network/container/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_cnns_host(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all Cloud Native Network Segmentation (CNNS) host audits.

        Args:
            params (dict): Query parameters.

        Example:
            >> pcce.audits.list_cnns_host()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = CNNSHostParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "firewall/network/host",
            params=validated_params,
        )

    def download_cnns_host(self, params: dict | None = None) -> BytesIO:
        """
        Returns the Cloud Native Network Segmentation (CNNS) host audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_cnns_host()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = CNNSHostParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "firewall/network/host/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_incident(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves a list of incidents that are not acknowledged (i.e., not in archived state)

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_incident()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = IncidentParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "incidents",
            params=validated_params,
        )

    def archive_incident(self, id: str, acknowledge: bool | None = True) -> None:
        """
        Acknowledges an incident and moves it to an archived state.

        Args:
            id (str): an Incident ID get from `incident_list()`.
            acknowledge (bool): Default is True, set to False if you want to unarchive.

        Example:
            >>> pcce.audits.archive_incident('637627beb2a8e98a1c36a9db')
        """
        self._patch(f"incidents/acknowledge/{id}", json={"acknowledge": acknowledge})

    def download_incident(self, params: dict | None = None) -> BytesIO:
        """
        Downloads a list of incidents which are not acknowledged (i.e., not in archived state) in CSV format.

        Args:
            params (dict): Query parameters.

            Example:
                >>> pcce.audits.download_incident()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = IncidentParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "incidents/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_kubernetes(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves events that occur in an integrated Kubernetes cluster that you configured for Prisma Cloud.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_kubernetes()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = KubernetesParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "kubernetes",
            params=validated_params,
        )

    def download_kubernetes(self, params: dict | None = None) -> BytesIO:
        """
        Returns the audit events data that occur in an integrated Kubernetes cluster that you configured for
            Prisma Cloud.

        Args:
            params (dict): Query parameters.

            Example:
                >>> pcce.audits.download_kubernetes()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = KubernetesParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "kubernetes/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_management(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves a list of all management audit events.

        Args:
            params (dict): Query parameters.

            Example:
                >>> pcce.audits.list_management()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ManagementParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "mgmt",
            params=validated_params,
        )

    def download_management(self, params: dict | None = None) -> BytesIO:
        """
        Returns the management audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_management()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ManagementParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "mgmt/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_management_filter(self, params: dict | None = None) -> dict:
        """
        Retrieves a list of management audit types from your environment. Use these filters to query management audit
            events.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_management_filter()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = ManagementParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "mgmt/filters",
            params=validated_params,
        )

    def list_runtime_app_embeded(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all app-embedded runtime audit events.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_runtime_app_embeded()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/app-embedded",
            params=validated_params,
        )

    def download_runtime_app_embeded(self, params: dict | None = None) -> BytesIO:
        """
        Returns the app-embedded runtime audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_runtime_app_embeded()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "runtime/app-embedded/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_runtime_container(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all container audit events when a runtime sensor such as process, network, file system, or system
            call detects an activity that deviates from the predictive model.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_runtime_container()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/container",
            params=validated_params,
        )

    def download_runtime_container(self, params: dict | None = None) -> BytesIO:
        """
        Returns the container audit events data in CSV format when a runtime sensor such as process, network, file
            system, or system call detects an activity that deviates from the predictive model.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_runtime_container()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "runtime/container/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_runtime_container_timeframe(self, params: dict | None = None) -> dict:
        """
        Retrieves the container audit events when a runtime sensor such as process, network, file system, or system
            call detects an activity that deviates from the predictive model for a specific time frame.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_runtime_container_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/container/timeslice",
            params=validated_params,
        )

    def list_runtime_file_integrity(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all audit events for file-integrity checks that are configured under host runtime rules.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_runtime_file_integrity()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeFileIntegrityParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/file-integrity",
            params=validated_params,
        )

    def download_runtime_file_integrity(self, params: dict | None = None) -> BytesIO:
        """
        Returns the audit events data in CSV format for file-integrity checks that are configured under host runtime
            rules.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_runtime_file_integrity()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeFileIntegrityParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get("runtime/file-integrity/download", params=validated_params, stream=True)
        return download(response=resp)

    def list_runtime_host(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves the runtime host audit events.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_runtime_host()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/host",
            params=validated_params,
        )

    def download_runtime_host(self, params: dict | None = None) -> BytesIO:
        """
        Returns the runtime host audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_runtime_host()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "runtime/host/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_runtime_host_timeframe(self, params: dict | None = None) -> dict:
        """
        Retrieves the runtime host audit events for a specific time frame.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_runtime_host_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/host/timeslice",
            params=validated_params,
        )

    def list_runtime_log_inspection(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all audit events for log inspection checks that are configured under host runtime rules.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_runtime_log_inspection()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeLogInspectionParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/log-inspection",
            params=validated_params,
        )

    def download_runtime_log_inspection(self, params: dict | None = None) -> BytesIO:
        """
        Returns the audit events data in CSV format for log inspection checks that are configured under host runtime
            rules.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_runtime_log_inspection()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeLogInspectionParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "runtime/log-inspection/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def list_runtime_serverless(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all scan events for any configured serverless functions in Prisma Cloud Compute.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_runtime_serverless()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeServerlessParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/serverless",
            params=validated_params,
        )

    def download_runtime_serverless(self, params: dict | None = None) -> BytesIO:
        """
        Returns the scan audit events data in CSV format for any configured serverless functions in Prisma Cloud
            Compute.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_runtime_serverless()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeServerlessParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "runtime/serverless/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)

    def get_runtime_serverless_timeframe(self, params: dict | None = None) -> dict:
        """
        Retrieves all scan events for any configured serverless functions in Prisma Cloud Compute for a specific time
            frame.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.get_runtime_serverless_timeframe()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = RuntimeServerlessTimeframeParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "runtime/serverless/timeslice",
            params=validated_params,
        )

    def list_trust(self, params: dict | None = None) -> list[dict]:
        """
        Retrieves all the trust audit events.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.list_trust()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = TrustParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        return self._get(
            "trust",
            params=validated_params,
        )

    def download_trust(self, params: dict | None = None) -> BytesIO:
        """
        Returns the trust audit events data in CSV format.

        Args:
            params (dict): Query parameters.

        Example:
            >>> pcce.audits.download_trust()
        """
        if params is None:  # pragma: no branch
            params = {}
        schema = TrustParamsSchema()
        errors = schema.validate(params)
        if errors:
            raise ValueError(f"Invalid parameters: {errors}")
        validated_params = schema.dump(schema.load(params))
        resp = self._get(
            "trust/download",
            params=validated_params,
            stream=True,
        )
        return download(response=resp)
