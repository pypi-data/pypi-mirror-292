"""
Feeds Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate

from .utils import PCCEDateTime


class RuleVulsSchema(Schema):
    """Rule Vuls Schema"""

    _id = fields.Str()
    max_version_inclusive = fields.Str(data_key="maxVersionInclusive")
    min_version_inclusive = fields.Str(data_key="minVersionInclusive")
    name = fields.Str()
    md5 = fields.Str()
    package = fields.Str()
    _type = fields.Str(
        data_key="type",
        validate=validate.OneOf(
            ["nodejs", "gem", "python", "jar", "package", "windows", "binary", "nuget", "go", "app", "unknown"]
        ),
    )


class VulsSchema(Schema):
    """Vuls Schema"""

    _id = fields.Str(metadata={"description": "ID is the custom vulnerabilities feed ID."})
    digest = fields.Str(metadata={"description": "Digest is an internal digest of the feed."})
    rules = fields.List(
        fields.Nested(RuleVulsSchema), metadata={"description": "Rules is the list of custom vulnerabilities rules."}
    )


class FeedMalwareSchema(Schema):
    """Feed Malware Schema"""

    allowed = fields.Bool(metadata={"description": "Allowed indicates if this signature is on the allowed list."})
    md5 = fields.Str()
    modified = fields.Int(metadata={"description": "Modified is the time the malware was added to the DB."})
    name = fields.Str()


class MalwareSchema(Schema):
    """Malware Schema"""

    _id = fields.Str(metadata={"description": "ID is the custom feed id."})
    digest = fields.Str(metadata={"description": "Digest is the internal custom vulnerabilities feed digest."})
    feed = fields.List(
        fields.Nested(FeedMalwareSchema), metadata={"description": "Feed is the list of custom malware signatures."}
    )
    modified = PCCEDateTime(metadata={"description": "Modified is the last time the custom feed was modified."})
