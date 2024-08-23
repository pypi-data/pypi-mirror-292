"""
Hosts Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields


class HostScanResultsParamsSchema(Schema):
    """Hosts Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    hostname = fields.List(fields.Str(), metadata={"description": "Filters the result based on hostnames."})
    distro = fields.List(fields.Str(), metadata={"description": "Filters the result based on OS distribution names."})
    compact = fields.Bool(
        metadata={
            "description": "Provides minimal image data. Information about vulnerabilities, compliance, and extended"
            "image metadata are skipped. Default is false."
        }
    )
    clusters = fields.List(fields.Str(), metadata={"description": "Filters the result based on cluster names."})
    compliance_ids = fields.List(
        fields.Int(data_key="complianceIDs"), metadata={"description": "Filters the result based on compliance IDs."}
    )
    compliance_rule_name = fields.Str(
        data_key="complianceRuleName",
        metadata={"description": "Filters the result based on applied compliance rule name."},
    )
    agentless = fields.Bool(
        metadata={"description": "Retrieves the host names that were scanned by the agentless scanner."}
    )
    csa = fields.Bool(metadata={"description": "Filters only images scanned by CSA."})
    stopped = fields.Bool(
        metadata={
            "description": "Retrieves the host names that were skipped during an agentless scan. Default is false."
        }
    )
    normalized_severity = fields.Bool(
        data_key="normalizedSeverity",
        metadata={
            "description": "Retrieves the result in the normalized form of low, medium, high,"
            "and critical based on vulnerability's severity level. Default is false."
        },
    )
