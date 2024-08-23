"""
Application Control Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields

from .utils import PCCEDateTime


class ApplicationSchema(Schema):
    """ApplicationSchema"""

    allowed_version = fields.List(
        fields.Str(),
        data_key="allowedVersions",
        metadata={
            "description": "Conditions represents a list of CVE rules (used to determine whether a CVE applies to"
            "a given package)"
        },
    )
    name = fields.Str(metadata={"description": "Name is the name of the application."})


class HostApplicationControlRuleSchema(Schema):
    """HostApplicationControlRuleSchema"""

    _id = fields.Int(metadata={"description": "ID is the ID of the rule."})
    applications = fields.List(
        fields.Nested(ApplicationSchema),
        metadata={"description": "Applications are rules configuring the desired effect per application."},
    )
    description = fields.Str(metadata={"description": "Description is the rule description."})
    disabled = fields.Bool(
        metadata={"description": "Indicates if the rule is currently disabled (true) or not (false)."}
    )
    modified = PCCEDateTime(metadata={"description": "Datetime when the rule was last modified."})
    name = fields.Str(metadata={"description": "Name of the rule."})
    notes = fields.Str(metadata={"description": "Free-form text."})
    owner = fields.Str(metadata={"description": "User who created or last modified the rule."})
    previous_name = fields.Str(
        data_key="previousName", metadata={"description": "Previous name of the rule. Required for rule renaming."}
    )
    severity = fields.Str(metadata={"description": "Severity is the rule's severity."})
