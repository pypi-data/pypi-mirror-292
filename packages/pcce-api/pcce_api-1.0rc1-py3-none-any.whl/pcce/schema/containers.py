from __future__ import annotations

from marshmallow import Schema, fields


class ScanResultParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    hostname = fields.List(fields.Str(), metadata={"description": "Hosts is used to filter containers by host."})
    image = fields.List(fields.Str(), metadata={"description": "Images is used to filter containers by image name."})
    image_id = fields.List(
        fields.Str(),
        data_key="imageId",
        metadata={"description": "ImageIDs is used to filter containers by image ids."},
    )
    id = fields.List(fields.Str(), metadata={"description": "IDs is used to filter container by container ID."})
    profile_id = fields.List(
        fields.Str(),
        data_key="profileId",
        metadata={"description": "ProfileIDs is used to filter container by runtime profile ID."},
    )
    namespaces = fields.List(fields.Str(), metadata={"description": "Namespaces are the namespaces to filter."})
    _fields = fields.List(
        fields.Str(), data_key="fields", metadata={"description": "Fields are used to fetch specific container field."}
    )
    firewall_supported = fields.Bool(
        data_key="firewallSupported",
        metadata={"description": "FirewallSupported is used to fetch containers with app firewall supported."},
    )
    clusters = fields.List(
        fields.Str(), metadata={"description": "Clusters is used to filter containers by cluster name."}
    )
    compliance_ids = fields.List(
        fields.Int(),
        data_key="complianceIDs",
        metadata={"description": "ComplianceIDs is used to filter containers by compliance IDs."},
    )
    compliance_rule_name = fields.Str(
        data_key="complianceRuleName",
        metadata={"description": "ComplianceRuleName is used to filter containers by applied compliance rule name."},
    )
    agentless = fields.Bool(
        metadata={
            "description": "Agentless indicates that we should return only containers that were scanned by an "
            "agentless scanner."
        }
    )
    csa = fields.Bool(
        metadata={"description": "CSA indicates that we should return only containers that were scanned by CSA."}
    )
