from __future__ import annotations

from marshmallow import Schema, fields, validate

from .utils import PCCEDateTime


class TASDropletsParamsSchema(Schema):
    """TAS Droplets Params Schema"""

    offset = fields.Int(
        meta_data={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _id = fields.List(fields.Str(), data_key="id", metadata={"description": "Retrieves a list of cloud function IDs."})
    cloud_controller_addresses = fields.List(
        fields.Str(),
        data_key="cloudControllerAddresses",
        metadata={"description": "Retrieves a list of cloud controller addresses that contains the cloud functions."},
    )
    runtime = fields.List(fields.Str(), metadata={"description": "Runtime is used to filter by runtime."})
    version = fields.List(
        fields.Str(), metadata={"description": "Filters the result based on cloud function's versions."}
    )
    function_layers = fields.List(
        fields.Str(),
        data_key="functionLayers",
        metadata={"description": "Filters the result based on AWS Lambda Layers."},
    )
    defended = fields.Bool(
        metadata={
            "description": "Filters result based on cloud functions that are connected and protected by a Defender."
        }
    )
    compliance_ids = fields.List(
        fields.Int(),
        data_key="complianceIDs",
        metadata={"description": "Filters result based on compliance IDs."},
    )
    compliance_rule_name = fields.Str(
        data_key="complianceRuleName",
        metadata={"description": "Filters the result based on applied compliance rule name."},
    )
    platform = fields.List(
        fields.Str(),
        metadata={
            "description": "Filters result based on platforms (OS and architecture) such as Windows, Linux ARM x64,"
            "Linux x86, and so on."
        },
    )
    normalized_severity = fields.Bool(
        data_key="normalizedSeverity",
        metadata={
            "description": "Retrieves the result in the normalized form of low, medium, high, and critical based on"
            "vulnerability's severity level. Default is false."
        },
    )


class ProgressTASDropletsParamsSchema(Schema):
    """Progress TAS Droplets Params Schema"""

    discovery = fields.Bool(meta={"description": "Discovery indicates whether the scan is in discovery phase."})
    error = fields.Str(metadata={"description": "Error is the error that happened during scan."})
    hostname = fields.Str(metadata={"description": "Hostname is the hostname for which the progress apply."})
    _id = fields.Str(data_key="id", metadata={"description": "ID is the ID of the entity being scanned."})
    scan_time = PCCEDateTime(data_key="scanTime", metadata={"description": "ScanTime is the time of scan."})
    scanned = fields.Int(metadata={"description": "Scanned is the number of entities for which the scan completed."})
    title = fields.Str(metadata={"description": "Title is the progress title (set by the scanning process)."})
    total = fields.Int(metadata={"description": "Total is the total amount of entities that should be scanned."})
    _type = fields.Str(
        data_key="type",
        validate=validate.OneOf(
            [
                "image",
                "ciImage",
                "container",
                "host",
                "agentlessHost",
                "registry",
                "serverlessScan",
                "ciServerless",
                "vm",
                "tas",
                "ciTas",
                "cloudDiscovery",
                "serverlessRadar",
                "serverlessAutoDeploy",
                "hostAutoDeploy",
                "codeRepo",
                "ciCodeRepo",
            ]
        ),
        metadata={"description": "ScanType displays the components for an ongoing scan"},
    )
