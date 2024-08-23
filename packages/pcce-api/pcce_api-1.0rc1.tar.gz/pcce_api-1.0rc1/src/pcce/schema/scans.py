"""
Scans Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields

from .utils import PCCEDateTime


class CIImageScansParamsSchema(Schema):
    """CI Image Scans Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _id = fields.Str(metadata={"description": "Scan ID used in the image layers fetch."})
    job_name = fields.List(fields.Str, data_key="jobName", metadata={"description": "Jenkins job name."})
    _type = fields.List(fields.Str, data_key="type", metadata={"description": "Scan type."})
    _pass = fields.Bool(
        data_key="pass", metadata={"description": "Indicates whether to filter on passed scans (true) or not (false)."}
    )
    build = fields.Str(metadata={"description": "Build number."})
    image_id = fields.Str(data_key="imageID", metadata={"description": "Image ID of scanned image."})
    layers = fields.Bool(metadata={"description": "Indicates if CVEs are mapped to image layer (true) or not (false)."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "Filters results by start datetime. Based on scan time."}
    )
    _to = PCCEDateTime(data_key="to", metadata={"description": "Filters results by end datetime. Based on scan time."})
    _fields = fields.List(fields.Str, data_key="fields", metadata={"description": "List of fields to retrieve."})
    filter_base_image = fields.Bool(
        data_key="filterBaseImage",
        metadata={
            "description": "Indicates if base image vulnerabilities are to be filtered (true) or not (false). Requires"
            "predefined base images that have already been scanned."
        },
    )


class ScansSchema(Schema):
    """ScanSchema"""

    _id = fields.Str(metadata={"description": "ID of the scan result."})
    build = fields.Str(metadata={"description": "CI build."})
    compliance_failure_summary = fields.Str(
        data_key="complianceFailureSummary", metadata={"description": "Scan compliance failure summary."}
    )
    entity_info = fields.Dict(
        data_key="entityInfo", metadata={"description": "Entity information associated with the scan."}
    )
    job_name = fields.Str(data_key="jobName", metadata={"description": "CI job name."})
    _pass = fields.Bool(
        data_key="pass", metadata={"description": "Indicates if the scan passed (true) or failed (false)."}
    )
    time = fields.DateTime(metadata={"description": "Time of the scan."})
    version = fields.Str(metadata={"description": "Scanner version."})
    vuln_failure_summary = fields.Str(
        data_key="vulnFailureSummary", metadata={"description": "Scan vulnerability failure summary."}
    )
