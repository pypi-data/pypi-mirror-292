"""
Groups
"""

from __future__ import annotations

from marshmallow import Schema, fields

from .utils import PCCEDateTime


class UserGroupSchema(Schema):
    username = fields.Str(metadata={"description": "Name of a user."})


class GroupSchema(Schema):
    """Group Schema"""

    _id = fields.Str(metadata={"description": "Group name."})
    group_id = fields.Str(
        data_key="groupId", metadata={"description": "Group identifier in the Azure SAML identification process."}
    )
    group_name = fields.Str(data_key="groupName", metadata={"description": "Group name."})
    last_modified = PCCEDateTime(
        data_key="lastModified", metadata={"description": "Datetime when the group was created or last modified."}
    )
    ldap_group = fields.Bool(
        data_key="ldapGroup", metadata={"description": "Indicates if the group is an LDAP group (true) or not (false)."}
    )
    oauth_group = fields.Bool(
        data_key="oauthGroup",
        metadata={"description": "Indicates if the group is an OAuth group (true) or not (false)."},
    )
    oidc_group = fields.Bool(
        data_key="oidcGroup",
        metadata={"description": "Indicates if the group is an OpenID Connect group (true) or not (false)."},
    )
    owner = fields.Str(metadata={"description": "User who created or modified the group."})
    permissions = fields.List(fields.Dict(), metadata={"description": "Permissions associated with the group."})
    role = fields.Str(metadata={"description": "Role of the group."})
    saml_group = fields.Bool(
        data_key="samlGroup", metadata={"description": "Indicates if the group is a SAML group (true) or not (false)."}
    )
    user = fields.List(fields.Nested(UserGroupSchema), metadata={"description": "Users associated with the group."})
