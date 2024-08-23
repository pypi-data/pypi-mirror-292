from __future__ import annotations

from marshmallow import Schema, fields, validate

from .utils import PCCEDateTime


# TODO Implement full schema
class CodereposCISchema(Schema):
    """CodereposCI"""

    _id = fields.Str(metadata={"description": "Scan report ID in the database."})
    collections = fields.List(fields.Str(), metadata={"description": "List of matching code repo collections."})
    compliance_risk_score = fields.Float(
        data_key="complianceRiskScore",
        metadata={"description": "Code repository's compliance risk score. Used for sorting."},
    )
    files = fields.Str(metadata={"description": "Scan result for each manifest file in the repository."})
    _pass = fields.Bool(data_key="pass", metadata={"description": "Indicates whether the scan passed or failed."})
    repository = fields.Str(metadata={"description": "Repository is the metadata for a code repository."})
    scan_time = PCCEDateTime(
        data_key="scanTime",
        metadata={
            "description": "Date/time when this repository was last scanned. The results might be from the DB"
            "and not updated if the repository contents have not changed."
        },
    )
    _type = fields.Str(
        data_key="type",
        validate=validate.OneOf(["github", "CI"]),
        metadata={
            "description": "CodeRepoProviderType is the type of provider for the code repository, e.g., GitHub, GitLab"
            "etc."
        },
    )
    update_time = PCCEDateTime(
        data_key="updateTime", metadata={"description": "Date/time when this repository was last updated."}
    )
    vuln_info = fields.Str(
        data_key="vulnInfo",
        metadata={"description": "ImageInfo contains image information collected during image scan."},
    )
    vulnerability_risk_score = fields.Float(
        data_key="vulnerabilityRiskScore",
        metadata={"description": "Code repository's CVE risk score. Used for sorting."},
    )
    vulnerable_files = fields.Int(
        data_key="vulnerableFiles",
        metadata={
            "description": "Counts how many files have vulnerabilities. Vulnerability info is calculated on demand."
        },
    )
