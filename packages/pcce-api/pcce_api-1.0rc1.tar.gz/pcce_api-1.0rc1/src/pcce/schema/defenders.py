"""
Defenders Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class DefendersParamsSchema(Schema):
    """DefendersParamsSchema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    hostname = fields.Str(metadata={"description": "Hostname is a name of a specific Defender to retrieve."})
    role = fields.List(fields.Str(), metadata={"description": "Roles are the defender API roles to filter."})
    connected = fields.Bool(
        metadata={
            "description": "Indicates whether to return only connected Defenders (true) or disconnected Defenders"
            "(false)."
        }
    )
    _type = fields.List(
        fields.Str(),
        data_key="type",
        metadata={"description": "Indicates the Defender types to return (e.g., docker, dockerWindows, cri, etc)."},
    )
    latest = fields.Bool(
        metadata={
            "description": "Indicates whether to return a list of Defenders that are running the latest version of"
            "Prisma Cloud (true) or defenders with older versions (false)."
        }
    )
    supported_version = fields.Bool(
        data_key="supportedVersion",
        metadata={"description": "SupportedVersion indicates only Defenders of supported versions should be fetched."},
    )
    cluster = fields.List(fields.Str(), metadata={"description": "Scopes the query by cluster name."})
    tas_cluster_ids = fields.List(
        fields.Str(), data_key="tasClusterIDs", metadata={"description": "Scopes the query by TAS cluster IDs."}
    )
    tas_blobstore_scanner = fields.Bool(
        data_key="tasBlobstoreScanner",
        metadata={
            "description": "Scopes the query by TAS blobstore scanning only Defenders (true) or TAS full coverage"
            "Defenders (false)."
        },
    )
    tas_foundations = fields.List(
        fields.Str(), data_key="tasFoundations", metadata={"description": "Scopes the query by TAS foundations."}
    )
    using_old_ca = fields.Bool(
        data_key="usingOldCA",
        metadata={"description": "Scopes the query to defenders which are using old certificate."},
    )
    using_expired_ca = fields.Bool(
        data_key="usingExpiredCA",
        metadata={"description": "Scopes the query to defenders which are using expired certificate."},
    )
    is_arm64 = fields.Bool(
        data_key="isARM64",
        metadata={
            "description": "Scopes the query by provider type Indicates whether to return only defenders running on "
            "ARM64 architecture."
        },
    )
    is_vpc_observer = fields.Bool(
        data_key="isVPCObserver",
        metadata={"description": "Indicates whether to return only defenders running as VPC Observer."},
    )


class DefendersSchema(Schema):
    annotations = fields.Dict(metadata={"description": "Annotations object."})
    bottlerocket = fields.Bool(
        metadata={"description": "Bottlerocket indicates whether to be deployed on a Bottlerocket Linux OS."}
    )
    cluster = fields.Str(metadata={"description": "Cluster is the Kubernetes or ECS cluster name."})
    collect_pod_labels = fields.Bool(
        data_key="collectPodLabels",
        metadata={"description": "CollectPodLabels indicates whether to collect pod-related labels resource labels."},
    )
    console_addr = fields.Str(
        data_key="consoleAddr",
        metadata={"description": "ConsoleAddr is the console address for defender communication."},
    )
    container_runtime = fields.Str(
        data_key="containerRuntime",
        metadata={"description": "ContainerRuntime represents the supported container runtime types."},
    )
    cpu_limit = fields.Int(
        data_key="cpuLimit",
        metadata={"description": "CPULimit is the CPU limit for the defender daemonset - optional."},
    )
    credential_id = fields.Str(
        data_key="credentialID", metadata={"description": "CredentialID is the name of the credential used."}
    )
    docker_socket_path = fields.Str(
        data_key="dockerSocketPath", metadata={"description": "DockerSocketPath is the path of the docker socket file."}
    )
    gke_autopilot = fields.Bool(
        data_key="gkeAutopilot",
        metadata={"description": "GKEAutopilot indicates the deployment is requested for GKE Autopilot."},
    )
    image = fields.Str(metadata={"description": "Image is the full daemonset image name."})
    istio = fields.Bool(metadata={"description": "MonitorIstio indicates whether to monitor Istio."})
    memory_limit = fields.Int(
        data_key="memoryLimit",
        metadata={"description": "MemoryLimit is a memory limit for the defender daemonset - optional."},
    )
    namespace = fields.Str(metadata={"description": "Namespace is the target daemonset namespaces."})
    node_selector = fields.Str(
        data_key="nodeSelector", metadata={"description": "NodeSelector is a key/value node selector."}
    )
    orchestration = fields.Str(metadata={"description": "Orchestration is the orchestration type."})
    priority_class_name = fields.Str(
        data_key="priorityClassName",
        metadata={"description": "PriorityClassName is the name of the priority class for the defender - optional."},
    )
    privileged = fields.Bool(metadata={"description": "Privileged indicates whether to run defenders as privileged."})
    project_id = fields.Str(
        data_key="projectID", metadata={"description": "ProjectID is the Kubernetes cluster project ID."}
    )
    proxy = fields.Dict(metadata={"description": "Proxy object."})
    region = fields.Str(metadata={"description": "Region is the Kubernetes cluster location region."})
    role_arn = fields.Str(
        data_key="roleARN",
        metadata={"description": "RoleARN is the role's ARN to associate with the created service account - optional."},
    )
    secrets_name = fields.Str(
        data_key="secretsname", metadata={"description": "SecretsName is the name of the secret to pull."}
    )
    selinux = fields.Bool(
        metadata={"description": "SelinuxEnforced indicates whether SELinux is enforced on the target host."}
    )
    service_accounts = fields.Bool(
        data_key="serviceaccounts",
        metadata={"description": "MonitorServiceAccounts indicates whether to monitor service accounts."},
    )
    talos = fields.Bool(
        metadata={"description": "Talos indicates if the daemonset is to be deployed on a Talos Linux k8s cluster."}
    )
    tolerations = fields.List(fields.Dict(), metadata={"description": "Tolerations object list."})
    unique_hostname = fields.Bool(
        data_key="uniqueHostname",
        metadata={"description": "UniqueHostname indicates whether to assign unique hostnames."},
    )


class FargateParamsSchema(Schema):
    console_addr = fields.Str(
        data_key="consoleaddr", metadata={"description": "ConsoleAddr is the remote console address."}
    )
    defender_type = fields.Str(
        data_key="defenderType",
        validate=validate.OneOf(
            [
                "none",
                "docker",
                "dockerWindows",
                "containerdWindows",
                "swarm",
                "daemonset",
                "serverLinux",
                "serverWindows",
                "cri",
                "fargate",
                "appEmbedded",
                "tas",
                "tasWindows",
                "serverless",
                "ecs",
            ]
        ),
        metadata={"description": "DefenderType is the type of the defender to create the install bundle for."},
    )
    interpreter = fields.Str(
        metadata={
            "description": "Interpreter is a custom interpreter set by the user to run the fargate defender entrypoint"
            "script."
        }
    )
    cloud_formation = fields.Bool(
        data_key="cloudFormation",
        metadata={
            "description": "CloudFormation indicates if the given fargate task definition is in Cloud Formation format."
        },
    )
    filesystem_monitoring = fields.Bool(
        data_key="filesystemMonitoring",
        metadata={"description": "FilesystemMonitoring is the filesystem monitoring flag."},
    )
    extract_entrypoint = fields.Bool(
        data_key="extractEntrypoint",
        metadata={"description": "ExtractEntrypoint indicates if entrypoint will be extracted automatically."},
    )
    registry_type = fields.Str(
        data_key="registryType",
        metadata={
            "description": "RegistryType is the registry type for fetching image details needed to create fargate"
            "task definition (e.g., dockerhub)."
        },
    )
    registry_credential_id = fields.Str(
        data_key="registryCredentialID",
        metadata={
            "description": "RegistryCredentialID of the credentials in the credentials store to use for authenticating"
            "with the registry."
        },
    )
    defender_image = fields.Str(
        data_key="defenderImage",
        metadata={
            "description": "DefenderImage is the full path to the Defender image, if not specified Prisma's private"
            "registry is used."
        },
    )
    defender_image_pull_secret = fields.Str(
        data_key="defenderImagePullSecret",
        metadata={
            "description": "DefenderImagePullSecret is the name of the secret required to pull the Defender image from"
            "private registry."
        },
    )


class AppEmbededDefenderSchema(Schema):
    """AppEnbededDefenderSchema"""

    app_id = fields.Str(
        data_key="appID",
        metadata={"description": "AppID identifies the app that the embedded app defender defender is protecting."},
    )
    console_addr = fields.Str(data_key="consoleAddr", metadata={"description": "ConsoleAddr is the console address."})
    data_folder = fields.Str(
        data_key="dataFolder",
        metadata={"description": "DataFolder is the path to the Twistlock data folder in the container."},
    )
    dockerfile = fields.Str(
        metadata={"description": "Dockerfile is the Dockerfile to embed AppEmbedded defender into."}
    )
    filesystem_monitoring = fields.Bool(
        data_key="filesystemMonitoring",
        metadata={"description": "FilesystemMonitoring is the filesystem monitoring flag."},
    )


class ServerlessDefenderSchema(Schema):
    """ServerlessDefenderSchema"""

    provider = fields.List(fields.Str(), metadata={"description": "CloudProvider specifies the cloud provider name."})
    proxy_ca = fields.Str(
        data_key="proxyCA", metadata={"description": "ProxyCA is the proxy’s CA certificate for Defender to trust."}
    )
    runtime = fields.List(
        fields.Str(),
        metadata={
            "description": "LambdaRuntimeType represents the runtime type of the "
            "serverless function. The constants used are taken from: https://docs.aws.amazon.com/lambda/latest/"
            "dg/API_CreateFunction.html#SSS-CreateFunction-request-Runtime"
        },
    )
