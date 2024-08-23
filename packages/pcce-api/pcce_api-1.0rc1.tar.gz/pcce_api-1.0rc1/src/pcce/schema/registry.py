"""
Registry Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate

from .credentials import CredentialSchema
from .utils import PCCEDateTime


class RegistryParamsSchema(Schema):
    """Registry Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    id = fields.List(fields.Str, metadata={"description": "Filters results by registry image."})
    image_id = fields.List(
        fields.Str,
        data_key="imageID",
        metadata={"description": "Filters the result by image IDs that are available in daemonset."},
    )
    repository = fields.List(
        fields.Str, metadata={"description": "Filters the result based on image repository names."}
    )
    registry = fields.List(fields.Str, metadata={"description": "Filters the result based on image registry names."})
    name = fields.List(fields.Str, metadata={"description": "Filters the result based on full image names."})
    layers = fields.Bool(
        metadata={"description": "Indicates whether the CVEs are mapped to an image layer. Default is false."}
    )
    compact = fields.Bool(
        metadata={
            "description": "Provides the minimal image data. Information about vulnerabilities, compliance, and"
            "extended image metadata are skipped. Default is false."
        }
    )
    filter_base_image = fields.Bool(
        data_key="filterBaseImage",
        metadata={
            "description": "Indicates whether to filter the base image for vulnerabilities. Requires predefined base"
            "images that have already been scanned. Default is false."
        },
    )
    normalized_severity = fields.Bool(
        data_key="normalizedSeverity",
        metadata={
            "description": "Retrieves the result in the normalized form of low, medium, high, and critical based on"
            "vulnerability's severity level. Default is false."
        },
    )


class WebhookRegistrySchema(Schema):
    """Webhook Registry Schema"""

    action = fields.Str(metadata={"description": "Action is the webhook action."})
    artifactory = fields.Dict(
        metadata={
            "description": "ArtifactoryWebhookRequest is an artifactory webhook request. Artifactory doesn't have"
            "native webhook support; instead, it comes as a plugin"
            "https://github.com/jfrog/artifactory-user-plugins/tree/master/webhook. The relevant fields in this "
            "struct were reverse engineered from the webhook groovy code and from the fields that were sent by a real"
            "artifactory environment."
        }
    )
    domain = fields.Str(
        metadata={
            "description": "Domain indicates the artifactory webhook domain (e.g., artifact, docker, build, etc). Used"
            "to avoid filter docker events."
        }
    )
    event_type = fields.Str(
        metadata={"description": "EventType is the artifactory webhook action performed (e.g., push)."}
    )
    type = fields.Str(metadata={"description": "Type is the event type (Harbor registry)."})


class ProgressRegistryParamsSchema(Schema):
    """ProgressRegistryParamsSchema"""

    on_demand = fields.Bool(
        data_key="onDemand",
        metadata={"description": "OnDemand indicates the requested progress is for an on-demand scan."},
    )
    registry = fields.Str(metadata={"description": "Registry is the image's registry."})
    repo = fields.Str(metadata={"description": "Repository is the image's repository."})
    tag = fields.Str(metadata={"description": "Tag is the image's tag."})
    digest = fields.Str(metadata={"description": "Digest is the image's digest."})


class TagRegistrySchema(Schema):
    """TagRegistrySchema"""

    digest = fields.Str(metadata={"description": "Image digest (requires V2 or later registry)."})
    id = fields.Str(metadata={"description": "ID of the image."})
    registry = fields.Str(metadata={"description": "Registry name to which the image belongs."})
    repo = fields.Str(metadata={"description": "Repository name to which the image belongs."})
    tag = fields.Str(metadata={"description": "Image tag."})


class GitlabRegistrySpecSchema(Schema):
    """GitlabRegistrySpecSchema"""

    excluded_group_ids = fields.List(fields.Str, data_key="excludedGroupIDs")
    group_ids = fields.List(fields.Str, data_key="groupIDs")
    project_ids = fields.List(fields.Str, data_key="projectIDs")
    user_id = fields.Str(data_key="userID")


class LabelAzureCloudMetadataSchema(Schema):
    """LabelAzureCloudMetadataSchema"""

    key = fields.Str(metadata={"description": "Label key."})
    source_name = fields.Str(
        data_key="sourceName",
        metadata={"description": "Source name (e.g., for a namespace, the source name can be 'twistlock')."},
    )
    source_type = fields.Str(
        data_key="sourceType",
        validate=validate.OneOf(["namespace", "deployment", "aws", "azure", "gcp", "oci"]),
        metadata={
            "description": "ExternalLabelSourceType indicates the source of the labels. Possible values: [namespace,"
            "deployment, aws, azure, gcp, oci]."
        },
    )
    timestamp = PCCEDateTime(metadata={"description": "Time when the label was fetched."})
    value = fields.Str(metadata={"description": "Value of the label."})


class AzureCloudMetadataSchema(Schema):
    """Azure Cloud Metadata Schema"""

    account_id = fields.Str(data_key="accountID", metadata={"description": "Cloud account ID."})
    aws_execution_env = fields.Str(
        data_key="awsExecutionEnv", metadata={"description": "AWS execution environment (e.g. EC2/Fargate)."}
    )
    image = fields.Str(metadata={"description": "Image name."})
    labels = fields.List(
        fields.Nested(LabelAzureCloudMetadataSchema), metadata={"description": "Labels associated with the instance."}
    )
    name = fields.Str(metadata={"description": "Instance name."})
    provider = fields.Str(
        validate=validate.OneOf(["aws", "azure", "gcp", "alibaba", "oci", "others"]),
        metadata={
            "description": "CloudProvider specifies the cloud provider name. Possible values: [aws, azure, gcp,"
            "alibaba, oci, others]."
        },
    )
    region = fields.Str(metadata={"description": "Instance region."})
    resource_id = fields.Str(data_key="resourceID", metadata={"description": "Unique ID of the resource."})
    resource_url = fields.Str(data_key="resourceURL", metadata={"description": "Server-defined URL for the resource."})
    type = fields.Str(metadata={"description": "Instance type."})
    vm_id = fields.Str(data_key="vmID", metadata={"description": "Azure unique VM ID."})
    vm_image_id = fields.Str(data_key="vmImageID", metadata={"description": "VMImageID holds the VM image ID."})


class SettingRegistrySchema(Schema):
    """SettingRegistrySchema"""

    azure_cloud_metadata = fields.Nested(
        AzureCloudMetadataSchema,
        data_key="azureCloudMetadata",
        metadata={"description": "the metadata for an instance running in a cloud provider (AWS/GCP/Azure)"},
    )
    ca_cert = fields.Str(
        data_key="caCert",
        metadata={"description": "CACert is the Certificate Authority that signed the registry certificate."},
    )
    cap = fields.Int(
        metadata={
            "description": "Specifies the maximum number of images from each repo to fetch and scan, sorted by most"
            "recently modified."
        }
    )
    collections = fields.List(
        fields.Str, metadata={"description": "Specifies the set of Defenders in-scope for working on a scan job."}
    )
    credential = fields.Nested(CredentialSchema, metadata={"description": "Credential object."})
    credential_id = fields.Str(
        data_key="credentialID",
        metadata={
            "description": "ID of the credentials in the credentials store to use for authenticating with the registry."
        },
    )
    excluded_repositories = fields.List(
        fields.Str, data_key="excludedRepositories", metadata={"description": "Repositories to exclude from scanning."}
    )
    excluded_tags = fields.List(
        fields.Str, data_key="excludedTags", metadata={"description": "Tags to exclude from scanning."}
    )
    gitlab_registry_spec = fields.Nested(
        GitlabRegistrySpecSchema,
        data_key="gitlabRegistrySpec",
        metadata={"description": "GitlabRegistrySpec represents a specification for registry scanning in GitLab"},
    )
    harbor_deployment_security = fields.Bool(
        data_key="harborDeploymentSecurity",
        metadata={
            "description": "Indicates whether the Prisma Cloud plugin uses temporary tokens provided by Harbor to scan"
            "images in projects where Harbor's deployment security setting is enabled."
        },
    )
    jfrog_repo_types = fields.List(
        fields.Str,
        data_key="jfrogRepoTypes",
        validate=validate.OneOf(["local", "remote", "virtual"]),
        metadata={
            "description": "JFrog Artifactory repository types to scan. Possible values: [local, remote, virtual]."
        },
    )
    namespace = fields.Str(
        metadata={
            "description": "IBM Bluemix namespace"
            "https://console.bluemix.net/docs/services/Registry/registry_overview.html#registry_planning."
        }
    )
    os = fields.Str(
        validate=validate.OneOf(["linux", "linuxARM64", "windows"]),
        metadata={
            "description": "RegistryOSType specifies the registry images base OS type. Possible values: [linux,"
            "linuxARM64, windows]."
        },
    )
    repository = fields.Str(metadata={"description": "Repositories to scan."})
    scanners = fields.Int(metadata={"description": "Number of Defenders that can be utilized for each scan job."})
    version = fields.Str(
        metadata={
            "description": "Registry type. Determines the protocol Prisma Cloud uses to communicate with the registry."
        }
    )
    version_pattern = fields.Str(
        data_key="versionPattern",
        metadata={
            "description": "Pattern heuristic for quickly filtering images by tags without having to query all images"
            "for modification dates."
        },
    )


class ScanRegistrySchema(Schema):
    """Scan Registry Schema"""

    on_demand_scan = fields.Bool(
        data_key="onDemandScan",
        metadata={"description": "OnDemandScan indicates whether to handle request using the on-demand scanner."},
    )
    scan_id = fields.Int(data_key="scanID", metadata={"description": "ScanID is the ID of the scan."})
    settings = fields.Nested(
        SettingRegistrySchema,
        metadata={"description": "RegistrySpecification contains information for connecting to local/remote registry"},
    )
    tag = fields.Nested(
        TagRegistrySchema,
        metadata={"description": "ImageTag represents an image repository and its associated tag or registry digest"},
    )
    _type = fields.Int(data_key="type", metadata={"description": "Type indicates the type of the scan request."})
