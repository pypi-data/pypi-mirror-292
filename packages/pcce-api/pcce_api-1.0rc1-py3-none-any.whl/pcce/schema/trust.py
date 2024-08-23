"""
Trust Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate

from .collections import CollectionSchema
from .utils import PCCEDateTime


class GroupTrustSchema(Schema):
    """Group Trust Schema"""

    _id = fields.Str(metadata={"description": "Name of the group."})
    disabled = fields.Bool(
        metadata={"description": "Indicates if the rule is currently disabled (true) or not (false)."}
    )
    images = fields.List(
        fields.Str(),
        metadata={"description": "Image names or IDs (e.g., docker.io/library/ubuntu:16.04 / SHA264@...)."},
    )
    layers = fields.List(
        fields.Str(),
        metadata={
            "description": "Filesystem layers. The image is trusted if its layers have a prefix of the trusted groups"
            "layer in the same order."
        },
    )
    modified = PCCEDateTime(metadata={"description": "Datetime when the rule was last modified."})
    name = fields.Str(metadata={"description": "Name of the rule."})
    notes = fields.Str(metadata={"description": "Free-form text."})
    owner = fields.Str(metadata={"description": "User who created or last modified the rule."})
    previous_name = fields.Str(
        data_key="previousName", metadata={"description": "Previous name of the rule. Required for rule renaming."}
    )


class RulePolicyTrustSchema(Schema):
    """Rule Policy Trust Schema"""

    allowed_groups = fields.List(
        fields.Str(),
        data_key="allowedGroups",
        metadata={"description": "AllowedGroups are the ids of the groups that are whitelisted by this rule."},
    )
    block_msg = fields.Str(
        data_key="blockMsg", metadata={"description": "PolicyBlockMsg represent the block message in a Policy"}
    )
    collections = fields.List(
        fields.Nested(CollectionSchema),
        metadata={"description": "Collections is a list of collections the rule applies to."},
    )
    denied_groups = fields.List(
        fields.Str(),
        data_key="deniedGroups",
        metadata={"description": "DeniedGroups are the ids of the groups that are blacklisted by this rule."},
    )
    disabled = fields.Bool(
        metadata={"description": "Indicates if the rule is currently disabled (true) or not (false)."}
    )
    effect = fields.Str(
        validate=validate.OneOf(["ignore", "alert", "block"]),
        metadata={"description": "Effect specifies relevant action for a vulnerability"},
    )
    modified = PCCEDateTime(metadata={"description": "Datetime when the rule was last modified."})
    name = fields.Str(metadata={"description": "Name of the rule."})
    notes = fields.Str(metadata={"description": "Free-form text."})
    owner = fields.Str(metadata={"description": "User who created or last modified the rule."})
    previous_name = fields.Str(
        data_key="previousName", metadata={"description": "Previous name of the rule. Required for rule renaming."}
    )


class PolicyTrustSchema(Schema):
    """Policy Trust Schema"""

    _id = fields.Str(metadata={"description": "ID is the trust group policy ID."})
    enabled = fields.Bool(metadata={"description": "Enabled indicates whether the policy is enabled."})
    rules = fields.List(
        fields.Nested(RulePolicyTrustSchema), metadata={"description": "Rules is the list of rules in the policy."}
    )


class TrustSchema(Schema):
    """Trust Schema"""

    groups = fields.List(fields.Nested(GroupTrustSchema), metadata={"description": "Groups are the trust groups."})
    policy = fields.Nested(PolicyTrustSchema, metadata={"description": "Policy represents the trust policy"})
