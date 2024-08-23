"""
Agentless Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields

from .credentials import CredentialSchema


class AgentlessSchema(Schema):
    """Agentless Schema"""

    credential = fields.Nested(
        CredentialSchema,
        metadata={"description": "Credential specifies the authentication data of an external provider"},
    )
    aws_region_type = fields.Str(
        data_key="awsRegionType",
        metadata={"description": "RegionType specifies the region type that runs the Amazon services"},
    )
    credential_id = fields.Str(
        data_key="credentialID", metadata={"description": "Specifies the ID for which the templates are generated."}
    )
