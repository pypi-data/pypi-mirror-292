from __future__ import annotations

from marshmallow import Schema, fields, validate

from .utils import PCCEDateTime


class PermissionSchema(Schema):
    project = fields.Str(metadata={"description": "Names of projects which the user can access."})
    collections = fields.List(fields.Str(), metadata={"description": "List of collections the user can access."})


class UserSchema(Schema):
    username = fields.Str(metadata={"description": "Username for authentication."})
    password = fields.Str(metadata={"description": "Password for authentication."})
    role = fields.Str(metadata={"description": "User role."})
    auth_type = fields.Str(
        data_key="authType",
        validate=validate.OneOf(["saml", "ldap", "basic", "oauth", "oidc"]),
        metadata={"description": "AuthType is the user authentication type"},
    )
    permissions = fields.List(
        fields.Nested(PermissionSchema), metadata={"description": "Permissions is a list of permissions"}
    )
    last_modified = PCCEDateTime(
        data_key="lastModified", metadata={"description": "Datetime when the user was created or last modified."}
    )
