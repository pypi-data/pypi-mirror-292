from __future__ import annotations

from marshmallow import Schema, fields


class VMImagesParamsSchema(Schema):
    offset = fields.Int(metadata={"description": "Offset for pagination."})
    limit = fields.Int(metadata={"description": "Limit for pagination."})
    sort = fields.Str(metadata={"description": "Sort order."})
    reverse = fields.Bool(metadata={"description": "Whether to reverse the sort order."})
    _id = fields.List(fields.Str(), data_key="id", metadata={"description": "List of VM image scan report IDs."})
    name = fields.List(fields.Str(), metadata={"description": "List of VM image scan report names."})
    credential = fields.List(fields.Str(), metadata={"description": "List of credentials."})
    distro = fields.List(fields.Str(), metadata={"description": "List of distributions."})
    release = fields.List(fields.Str(), metadata={"description": "List of releases."})
    image_type = fields.List(fields.Str(data_key="imageType"), metadata={"description": "List of image types."})
    compliance_ids = fields.List(
        fields.Int(data_key="complianceIDs"), metadata={"description": "List of compliance IDs."}
    )
    compliance_rule_name = fields.Str(
        data_key="complianceRuleName", metadata={"description": "Name of the compliance rule."}
    )
    normalized_severity = fields.Bool(
        data_key="normalizedSeverity", metadata={"description": "Whether to normalize the severity."}
    )
