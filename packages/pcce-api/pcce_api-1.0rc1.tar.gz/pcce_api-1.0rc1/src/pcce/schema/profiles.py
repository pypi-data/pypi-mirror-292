"""
Profiles Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields


class AppEmbeddedProfileParamsSchema(Schema):
    """AppEmbedded Profile Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    id = fields.List(fields.Str, metadata={"description": "IDs is the runtime profile id filter."})
    app_id = fields.List(
        fields.Str, data_key="appID", metadata={"description": "AppIDs is the app embedded profile app IDs filter."}
    )
    container = fields.List(fields.Str, metadata={"description": "Containers is the app embedded container filter."})
    image = fields.List(fields.Str, metadata={"description": "Images is the app embedded images filter."})
    cluster = fields.List(fields.Str, metadata={"description": "Clusters is the app embedded clusters filter."})
    image_id = fields.List(
        fields.Str, data_key="imageID", metadata={"description": "ImageIDs is the app embedded image IDs filter."}
    )


class RuntimeProfileParamsSchema(Schema):
    """Runtime Profile Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    id = fields.List(fields.Str, metadata={"description": "IDs is the runtime profile id filter."})
    os = fields.List(fields.Str, metadata={"description": "OS is the service runtime profile OS filter."})
    state = fields.List(fields.Str, metadata={"description": "States is the runtime profile state filter."})
    image_id = fields.List(
        fields.Str, data_key="imageID", metadata={"description": "ImageIDs is the runtime profile image id filter."}
    )
    image = fields.List(fields.Str, metadata={"description": "Images is the runtime profile image filter."})
    host_name = fields.List(
        fields.Str, data_key="hostName", metadata={"description": "Hosts is the runtime profile hostname filter."}
    )
    namespace = fields.List(
        fields.Str, metadata={"description": "Namespaces is the runtime profile k8s namespace filter."}
    )
    cluster = fields.List(fields.Str, metadata={"description": "Clusters is the runtime profile k8s cluster filter."})
