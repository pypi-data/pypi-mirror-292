from __future__ import annotations

from marshmallow import Schema, fields


class DiscoveryResultParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    provider = fields.List(fields.Str(), metadata={"description": "Provider is the provider filter."})
    credential_id = fields.List(
        fields.Str(), data_key="credentialID", metadata={"description": "CredentialID is the account filter."}
    )
    service_type = fields.List(
        fields.Str(), data_key="serviceType", metadata={"description": "ServiceType is the service type filter."}
    )
    registry = fields.List(fields.Str(), metadata={"description": "Registry is the registry filter."})
    account_name = fields.List(
        fields.Str(), data_key="accountName", metadata={"description": "AccountName is the account name filter."}
    )
    agentless = fields.Bool(metadata={"description": "Agentless is the agentless filter."})


class DiscoveryEntitiesParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    provider = fields.List(fields.Str(), metadata={"description": "Provider is the provider filter."})
    credential_id = fields.List(
        fields.Str(), data_key="credentialID", metadata={"description": "CredentialID is the account filter."}
    )
    service_type = fields.List(
        fields.Str(), data_key="serviceType", metadata={"description": "ServiceType is the service type filter."}
    )
    registry = fields.List(fields.Str(), metadata={"description": "Registry is the registry filter."})
    account_name = fields.List(
        fields.Str(), data_key="accountName", metadata={"description": "AccountName is the account name filter."}
    )
    defended = fields.Bool(metadata={"description": "Defended is the defended filter."})


class DiscoveryVMsParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    provider = fields.List(fields.Str(), metadata={"description": "Provider is the provider filter."})
    has_defended = fields.Bool(
        metadata={"description": "HasDefender indicates only VMs with or without a defender should return."}
    )
