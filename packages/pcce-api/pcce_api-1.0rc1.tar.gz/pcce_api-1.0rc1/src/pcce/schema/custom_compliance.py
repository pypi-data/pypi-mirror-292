from __future__ import annotations

from marshmallow import Schema, fields

from .utils import PCCEDateTime


class CustomComplianceSchema(Schema):
    """Custom Compliance Schema"""

    _id = fields.Int(metadata={"description": "ID is the compliance check ID."})
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
    script = fields.Str(metadata={"description": "Script is the custom check script."})
    severity = fields.Str(metadata={"description": "Severity is the custom check defined severity."})
    title = fields.Str(metadata={"description": "Title is the custom check title."})
