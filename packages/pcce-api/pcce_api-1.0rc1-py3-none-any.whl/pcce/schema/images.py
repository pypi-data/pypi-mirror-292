"""
Images Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields


class ImageParamsSchema(Schema):
    """Images Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _id = fields.List(fields.Str(), data_key="id", metadata={"description": "Filters the result based on image IDs."})
    hostname = fields.List(fields.Str(), metadata={"description": "Filters the result based on hostnames."})
    repository = fields.List(
        fields.Str(), metadata={"description": "Filters the result based on image repository names."}
    )
    registry = fields.List(fields.Str(), metadata={"description": "Filters the result based on image registry names."})
    _fields = fields.List(fields.Str(), data_key="fields", metadata={"description": "List of fields to retrieve."})
    name = fields.List(fields.Str(), metadata={"description": "Filters the result based on image names."})
    layers = fields.Bool(
        metadata={"description": "Indicates whether the CVEs are mapped to a specific image layer. Default is false."}
    )
    filter_base_image = fields.Bool(
        data_key="filterBaseImage",
        metadata={
            "description": "Indicates whether to filter the base image for vulnerabilities. Requires predefined base"
            "images that have already been scanned. Default is false."
        },
    )
    compact = fields.Bool(
        metadata={
            "description": "Provides the minimal image data. Information about vulnerabilities, compliance, and"
            "extended image metadata are skipped. Default is false."
        }
    )
    trust_statuses = fields.List(
        fields.Str(data_key="trustStatuses"),
        metadata={
            "description": "Filters the result based on whether an image is trusted or not trusted by a trusted image"
            "policy. Use filters: trusted or untrusted."
        },
    )
    clusters = fields.List(fields.Str(), metadata={"description": "Filters the result based on cluster names."})
    compliance_ids = fields.List(
        fields.Int(data_key="complianceIDs"), metadata={"description": "Filters the result by compliance IDs."}
    )
    compliance_rule_name = fields.Str(
        data_key="complianceRuleName",
        metadata={"description": "Filters the result based on applied compliance rule name."},
    )
    app_embedded = fields.Bool(
        data_key="appEmbedded",
        metadata={
            "description": "Filters the result based on whether the images are scanned by App-Embedded Defenders."
            "Default is false."
        },
    )
    normalized_severity = fields.Bool(
        data_key="normalizedSeverity",
        metadata={
            "description": "Retrieves the result in the normalized form of low, medium, high, and critical based on"
            "vulnerability's severity level. Default is false."
        },
    )
    agentless = fields.Bool(
        metadata={
            "description": "Indicates whether to retrieve host names that are scanned by agentless scanner."
            "Default is false."
        }
    )
    csa = fields.Bool(metadata={"description": "Filters only images scanned by CSA."})
