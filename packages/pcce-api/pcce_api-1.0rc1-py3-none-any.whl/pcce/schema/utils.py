from __future__ import annotations

from datetime import datetime

from marshmallow import fields


class PCCEDateTime(fields.DateTime):
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.strftime("%Y-%m-%dT%H:%M:%S.%f%z")[:23] + value.strftime("%Y-%m-%dT%H:%M:%S.%f%z")[26:]

    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f%z")
        except ValueError:
            self.make_error("validator_failed", input=value)
        return super()._deserialize(value, attr, data, **kwargs)


def get_field_info(field):
    description = field.metadata.get("description", "No description")
    field_type = field.__class__.__name__
    required = field.required

    field_info = {"type": field_type, "description": description, "required": required}

    # Handle nested fields
    if isinstance(field, fields.Nested):
        field_info["schema"] = get_schema_info(field.schema)
    elif isinstance(field, fields.List):
        list_field = field.inner
        if isinstance(list_field, fields.Nested):
            field_info["items"] = get_schema_info(list_field.schema)
        else:
            field_info["items"] = {"type": list_field.__class__.__name__}

    return field_info


def get_schema_info(schema):
    schema_info = {"title": schema.__class__.__name__, "type": "object", "properties": {}, "required": []}

    for field_name, field in schema.fields.items():
        field_info = get_field_info(field)

        schema_info["properties"][field_name] = field_info

        if field_info["required"]:
            schema_info["required"].append(field_name)

    return schema_info
