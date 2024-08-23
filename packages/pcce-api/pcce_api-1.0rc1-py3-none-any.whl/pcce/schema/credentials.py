from __future__ import annotations

from marshmallow import Schema, fields
from marshmallow import validate as v

from .utils import PCCEDateTime


class CredentialsParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    ids = fields.List(fields.Str(), metadata={"description": "IDs are the credential IDs to filter."})
    cloud = fields.Bool(
        metadata={
            "description": "Cloud indicates whether to fetch cloud credentials (AWS/GCP/OCI/Azure) or other types "
            "of credentials."
        }
    )
    external = fields.Bool(
        metadata={"description": "External indicates whether to fetch credentials imported from Prisma."}
    )
    auto_imported = fields.Bool(
        data_key="autoImported",
        metadata={
            "description": "AutoImported indicates whether to fetch credentials imported from Prisma automatically."
        },
    )


class TokenSchema(Schema):
    encrypted = fields.Str(metadata={"description": "Specifies an encrypted value of the secret"})
    plain = fields.Str(metadata={"description": "Specifies the plain text value of the secret."})


class APITokenSchema(TokenSchema):
    pass


class AzureSPInfoSchema(Schema):
    client_id = fields.Str(data_key="clientId", metadata={"description": "ClientID is the client identifier."})
    mi_type = fields.Str(data_key="miType", validate=v.OneOf(["user-assigned", "system-assigned"]))
    subscription_id = fields.Str(
        data_key="subscriptionId",
        metadata={
            "description": "SubscriptionID is a GUID that uniquely identifies the subscription to use Azure services."
        },
    )
    tenant_id = fields.Str(
        data_key="tenantId",
        metadata={"description": "TenantID is the ID of the AAD directory in which the application was created."},
    )


class OciCredSchema(Schema):
    fingerprint = fields.Str(metadata={"description": "Fingerprint is the public key signature."})
    tenancy_id = fields.Str(data_key="tenancyId", metadata={"description": "TenancyID is the OCID of the tenancy."})


class SecretSchema(Schema):
    encrypted = fields.Str(metadata={"description": "Specifies an encrypted value of the secret"})
    plain = fields.Str(metadata={"description": "Specifies the plain text value of the secret."})


class TokensSchema(Schema):
    aws_access_key_id = fields.Str(
        data_key="awsAccessKeyId", metadata={"description": "Specifies a temporary access key."}
    )
    aws_secret_access_key = fields.Nested(
        TokenSchema,
        data_key="awsSecretAccessKey",
        description="Secret Stores the plain and encrypted version of a value. The plain version is not stored in a \
        database",
    )
    duration = fields.Int(metadata={"description": "Specifies a duration for the token."})
    expiration_time = PCCEDateTime(
        data_key="expirationTime", metadata={"description": "Specifies an expiration time for the token."}
    )
    token = fields.Nested(
        TokenSchema,
        metadata={
            "description": "Secret Stores the plain and encrypted version of a value. The plain version is not stored"
            "in a database"
        },
    )


class CredentialSchema(Schema):
    _id = fields.Str()
    account_guid = fields.Str(
        data_key="accountGUID", metadata={"description": "Specifies the unique ID for an IBM Cloud account."}
    )
    account_id = fields.Str(
        data_key="accountID",
        metadata={
            "description": "Specifies the account identifier. Example: a username, access key, account GUID, and so on."
        },
    )
    account_name = fields.Str(
        data_key="accountName", metadata={"description": "Specifies the name of the cloud account."}
    )
    api_token = fields.Nested(
        APITokenSchema,
        data_key="apiToken",
        metadata={
            "description": "Secret Stores the plain and encrypted version of a value. The plain version is not"
            "stored in a database"
        },
    )
    azure_sp_info = fields.Nested(
        AzureSPInfoSchema,
        data_key="azureSPInfo",
        metadata={
            "description": "AzureSPInfo contains the Azure credentials needed for certificate based authentications"
        },
    )
    ca_cert = fields.Str(
        data_key="caCert",
        metadata={"description": "Specifies the CA certificate for a certificate-based authentication."},
    )
    cloud_provider_account_id = fields.Str(
        data_key="cloudProviderAccountID", metadata={"description": "Specifies the cloud provider account ID."}
    )
    created = PCCEDateTime(
        metadata={
            "description": "Specifies the time when the credential was created (or, when the account ID was changed"
            "for AWS)"
        }
    )
    description = fields.Str(metadata={"description": "Specifies the description for a credential."})
    external = fields.Bool(
        metadata={
            "description": "Indicates whether the credential is external. Available values are: true: external"
            "false: Not external."
        }
    )
    _global = fields.Bool(
        data_key="global",
        metadata={
            "description": "Indicates whether the credential scope is global. Available values are: true: Global"
            "false: Not Global Note: For GCP, the credential scope is the organization."
        },
    )
    last_modified = PCCEDateTime(
        data_key="lastModified", metadata={"description": "Specifies the time when the credential was last modified."}
    )
    oci_cred = fields.Nested(
        OciCredSchema,
        data_key="ociCred",
        metadata={"description": "OCICred are additional parameters required for OCI credentials"},
    )
    owner = fields.Str(metadata={"description": "Specifies the user who created or modified the credential."})
    prisma_last_modified = fields.Int(
        data_key="prismaLastModified",
        metadata={"description": "Specifies the time when the account was last modified by Prisma Cloud Compute."},
    )
    role_arn = fields.Str(
        data_key="roleArn",
        metadata={"description": "Specifies the Amazon Resource Name (ARN) of the role to be assumed."},
    )
    secret = fields.Nested(
        SecretSchema,
        metadata={
            "description": "Secret Stores the plain and encrypted version of a value. The plain version is not"
            "stored in a database"
        },
    )
    skip_verify = fields.Bool(
        data_key="skipVerify",
        metadata={"description": "Indicates whether to skip the certificate verification in TLS communication."},
    )
    sts_endpoints = fields.List(
        fields.Str(),
        data_key="stsEndpoints",
        metadata={"description": "Specifies a list of specific endpoints for use in STS sessions in various regions."},
    )
    tokens = fields.Nested(
        TokensSchema,
        metadata={
            "description": "TemporaryToken is a temporary session token for cloud provider APIs"
            "AWS - https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp.html"
            "GCP - https://cloud.google.com/iam/docs/creating-short-lived-service-account-credentials"
            "Azure - https://docs.microsoft.com/en-us/azure/active-directory/manage-apps/what-is-single-sign-on"
        },
    )
    _type = fields.Str(
        data_key="type",
        validate=v.OneOf(
            [
                "aws",
                "azure",
                "gcp",
                "ibmCloud",
                "oci",
                "apiToken",
                "githubToken",
                "githubEnterpriseToken",
                "basic",
                "dtr",
                "kubeconfig",
                "certificate",
                "gitlabToken",
            ]
        ),
        metadata={"description": "Type specifies the credential type"},
    )
    url = fields.Str(metadata={"description": "Specifies the base server URL."})
    use_aws_role = fields.Bool(
        data_key="useAWSRole",
        metadata={
            "description": "Indicates whether to authenticate using the IAM Role attached to the instance."
            "Available values are: true: Authenticate with the attached credentials false:"
            "Do not authenticate with the attached credentials"
        },
    )
    use_sts_regional_endpoint = fields.Bool(
        data_key="useSTSRegionalEndpoint",
        metadata={
            "description": "Indicates whether to use the regional STS endpoint for an STS session."
            "Available values are: true: Use the regional STS false: Do not use the regional STS."
        },
    )
