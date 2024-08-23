from __future__ import annotations

from marshmallow import Schema, fields

from .utils import PCCEDateTime


class CollectionSchema(Schema):
    name = fields.Str(required=True, metadata={"description": "Collection name. Must be unique."})
    account_ids = fields.List(fields.Str(), data_key="accountIDs", metadata={"description": "List of account IDs."})
    app_ids = fields.List(fields.Str(), data_key="appIDs", metadata={"description": "List of application IDs."})
    clusters = fields.List(fields.Str(), metadata={"description": "List of Kubernetes cluster names."})
    code_repos = fields.List(fields.Str(), data_key="codeRepos", metadata={"description": "List of code repositories."})
    color = fields.Str(metadata={"description": "Color is a hexadecimal representation of color code value."})
    containers = fields.List(fields.Str(), metadata={"description": "List of containers."})
    description = fields.Str(metadata={"description": "Free-form text."})
    functions = fields.List(fields.Str(), metadata={"description": "List of functions."})
    hosts = fields.List(fields.Str(), metadata={"description": "List of hosts."})
    images = fields.List(fields.Str(), metadata={"description": "List of images."})
    labels = fields.List(fields.Str(), metadata={"description": "List of labels."})
    modified = PCCEDateTime(metadata={"description": "Datetime when the collection was last modified."})
    namespaces = fields.List(fields.Str(), metadata={"description": "List of Kubernetes namespaces."})
    owner = fields.Str(metadata={"description": "User who created or last modified the collection."})
    prisma = fields.Bool(metadata={"description": "Indicates whether this collection originates from Prisma Cloud."})
    system = fields.Bool(
        metadata={
            "description": "Indicates whether this collection was created by the system (i.e., a non user) or a real"
            "user."
        }
    )
