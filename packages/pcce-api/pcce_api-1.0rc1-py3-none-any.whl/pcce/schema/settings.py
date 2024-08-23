"""
Settings Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class TASSettingsSchema(Schema):
    """TAS Settings Schema"""

    cap = fields.Int(metadata={"description": "Cap indicates only the last k images should be fetched."})
    cloud_controller_address = fields.Str(
        data_key="cloudControllerAddress",
        metadata={"description": "CloudControllerAddress is the address of the local cloud controller in TAS env."},
    )
    hostname = fields.Str(
        metadata={"description": "Hostname is the hostname of the defender that is used as the blobstore scanner."}
    )
    pattern = fields.Str(metadata={"description": "Pattern is the droplet name."})
    remote = fields.Bool(metadata={"description": "Remote indicates whether the blobstore is remote or local."})


class VMImageSettingsSchema(Schema):
    """VM Image Settings Schema"""

    version = fields.Str(validate=validate.OneOf(["aws"]))
    region = fields.Str()
    collections = fields.List(fields.Dict)
    cap = fields.Int(
        metadata={
            "description": "Specifies the maximum number of images to fetch and scan, ordered by most recently modified"
        }
    )
    console_addr = fields.Str(
        data_key="consoleAddr",
        metadata={
            "description": "Network-accessible address that Defender can use to publish scan results to Console."
        },
    )
    credential_id = fields.Str(
        data_key="credentialID",
        metadata={
            "description": "ID of the credentials in the credentials store to use for authenticating with the cloud"
            "provider."
        },
    )
    enable_secure_boot = fields.Bool(
        data_key="enableSecureBoot",
        metadata={
            "description": "EnableSecureBoot indicates secure boot should be enabled for the instance launched for"
            "scanning (currently only supported with GCP)."
        },
    )
    excluded_images = fields.List(
        fields.Str,
        data_key="excludedImages",
        metadata={"description": "Images to exclude from scanning."},
    )
    gcp_project_id = fields.Str(
        data_key="gcpProjectID",
        metadata={
            "description": "GCP project ID to use for listing VM images instead of the default associated with the GCP"
            "credential (optional)."
        },
    )
    image_type = fields.Str(
        data_key="imageType",
        metadata={
            "description": "ImageType is the type of a VM image. For example, in the case of Azure this is one of"
            "marketplace/managed/gallery."
        },
    )
    images = fields.List(fields.Str, metadata={"description": "The names of images to scan."})
    instance_type = fields.Str(
        data_key="instanceType",
        metadata={
            "description": "InstanceType is the instance type to use for the instance launched for scanning. For"
            "example, the default instance type for AWS is 'm4.large'."
        },
    )
    labels = fields.List(fields.Str, metadata={"description": "The labels to use to target images to scan."})
    region = fields.Str(metadata={"description": "Cloud provider region."})
    scanners = fields.Int(metadata={"description": "Number of Defenders that can be utilized for each scan job."})
    subnet_id = fields.Str(
        data_key="subnetID",
        metadata={
            "description": "SubnetID is the network subnet ID to use for the instance launched for scanning. Default"
            "value is empty string, which represents the default subnet in the VPC."
        },
    )
    vpc_id = fields.Str(
        data_key="vpcID",
        metadata={
            "description": "VPCID is the network VPC ID to use for the instance launched for scanning. Default value"
            "is empty string, which represents the default VPC in the region."
        },
    )
    zone = fields.Str(
        metadata={
            "description": "Cloud provider zone (part of a region). On GCP, designates in which zone to deploy the VM"
            "scan instance."
        }
    )
