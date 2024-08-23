"""
Tags Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class VulnTagSchema(Schema):
    """Vuln Tag Schema"""

    _id = fields.Str(
        data_key="id", metadata={"description": "Specifies the Common Vulnerability and Exposures (CVE) ID."}
    )
    comment = fields.Str(metadata={"description": "Adds a comment."})
    check_base_layer = fields.Bool(
        data_key="checkBaseLayer",
        metadata={
            "description": "(Applies only to the resource type 'image') Checks whether the base layer in an image is"
            "the resource image."
        },
    )
    package_name = fields.Str(
        data_key="packageName",
        metadata={
            "description": "Specifies the source or the binary package name where the vulnerability is found. Use the"
            "source package name for tagging if only source package exists. Use the wildcard * for tagging all the"
            "packages."
        },
    )
    resource_type = fields.Str(
        data_key="resourceType",
        validate=validate.OneOf(["image", "host", "function", "codeRepo", ""]),
        metadata={
            "description": "TagType specifies the resource type for tagging where the vulnerability is found. Use the"
            "wildcard * to apply the tag to all the resource types where the vulnerability is found"
        },
    )
    resources = fields.List(
        fields.Str(),
        metadata={
            "description": "(Required when you define the resource type) Specifies the resources for tagging where the"
            "vulnerability is found. Either specify the resource names separated by a comma or use the wildcard * to"
            "apply the tag to all the resources where the vulnerability is found."
        },
    )


class TagSchema(Schema):
    """Tag Schema"""

    color = fields.Str(metadata={"description": "Color is a hexadecimal representation of color code value"})
    description = fields.Str(metadata={"description": "Description is the tag description."})
    name = fields.Str(metadata={"description": "Name is the tag name."})
    vulns = fields.List(fields.Nested(VulnTagSchema), metadata={"description": "Vulns are the tagged vulnerabilities."})
