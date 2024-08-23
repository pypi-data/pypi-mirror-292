"""
Sandbox Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate

from .utils import PCCEDateTime


class ProcsSandboxSchema(Schema):
    """ProcsSandboxSchema"""

    command = fields.Str(metadata={"description": "Command is the command line."})
    md5 = fields.Str(metadata={"description": "MD5 is the md5 hash for the process binary."})
    parent = fields.Nested(
        lambda: ProcsSandboxSchema(),
        exclude=("parent",),
        metadata={"description": "ProcessInfo holds process information"},
    )
    path = fields.Str(metadata={"description": "Path is the binary path."})
    time = PCCEDateTime(metadata={"description": "Time is the process start time."})
    user = fields.Str(metadata={"description": "User is the username/id."})


class ConnectionSandboxSchema(Schema):
    """ConnectionSandboxSchema"""

    country_code = fields.Str(
        data_key="countryCode", metadata={"description": "CountryCode is the country code for the network IP."}
    )
    ip = fields.Str(metadata={"description": "IP is the network IP."})
    port = fields.Int(metadata={"description": "Port is the network port."})
    process = fields.Nested(
        ProcsSandboxSchema, metadata={"description": "Process is the process object associated with the connection."}
    )
    protocol = fields.Str(metadata={"description": "Protocol is the transport layer protocol (UDP / TCP)."})
    time = PCCEDateTime(metadata={"description": "Time is the event time."})


class DNSSandboxSchema(Schema):
    """DNSSandboxSchema"""

    country_code = fields.Str(
        data_key="countryCode", metadata={"description": "CountryCode is the country code for the network IP."}
    )
    domain_name = fields.Str(
        data_key="domainName", metadata={"description": "DomainName is the domain name for a DNS query."}
    )
    domain_type = fields.Str(
        data_key="domainType", metadata={"description": "DomainType is the domain type for a DNS query."}
    )
    ip = fields.Str(metadata={"description": "IP is the network IP."})
    process = fields.Nested(
        ProcsSandboxSchema, metadata={"description": "Process is the process object associated with the DNS query."}
    )
    time = PCCEDateTime(metadata={"description": "Time is the event time."})


class FilesystemSandboxSchema(Schema):
    """FilesystemSandboxSchema"""

    access_type = fields.Str(
        data_key="accessType",
        validate=validate.OneOf(["open", "modify", "create"]),
        metadata={"description": "Type of accessing a file. Possible values: [open, modify, create]"},
    )
    path = fields.Str(metadata={"description": "The file path."})
    process = fields.Nested(
        ProcsSandboxSchema,
        metadata={"description": "The process object associated with the filesystem event."},
    )
    time = PCCEDateTime(metadata={"description": "The event time."})


class EventFindingSandboxSchema(Schema):
    """EventFindingSandboxSchema"""

    description = fields.Str(metadata={"description": "Description describes what happened in the event."})
    time = PCCEDateTime(metadata={"description": "Time is the time of event detection."})


class FindingSandboxSchema(Schema):
    """FindingSandboxSchema"""

    description = fields.Str(metadata={"description": "Description is the finding description."})
    events = fields.List(
        fields.Nested(EventFindingSandboxSchema),
        metadata={"description": "Events is the list of events associated with the finding."},
    )
    severity = fields.Str(
        validate=validate.OneOf(["critical", "high", "medium", "low"]),
        metadata={"description": "Finding severity level. Possible values: [critical, high, medium, low]"},
    )
    time = PCCEDateTime(metadata={"description": "Time is the detection time (time of triggering event)."})
    _type = fields.Str(
        data_key="type",
        validate=validate.OneOf(
            [
                "dropper",
                "modifiedBinary",
                "executableCreation",
                "filelessExecutableCreation",
                "wildFireMalware",
                "verticalPortScan",
                "cryptoMiner",
                "suspiciousELFHeader",
                "kernelModule",
                "modifiedBinaryExecution",
                "filelessExecution",
            ]
        ),
        metadata={"description": "A unique sandbox-detected finding type."},
    )


class ListeningSandboxSchema(Schema):
    """ListeningSandboxSchema"""

    port = fields.Int(metadata={"description": "Port is the network port."})
    process = fields.Nested(
        ProcsSandboxSchema, metadata={"description": "ProcessEvent represents a process event during sandbox scan"}
    )
    time = PCCEDateTime(metadata={"description": "Time is the event time."})


class SuspiciousFileSandboxSchema(Schema):
    """SuspiciousFileSandboxSchema"""

    container_path = fields.Str(
        data_key="containerPath",
        metadata={"description": "ContainerPath is the path of the file in the running container."},
    )
    created = fields.Bool(metadata={"description": "Created indicates if the file was created during runtime."})
    md5 = fields.Str(metadata={"description": "MD5 is the file MD5 hash."})
    path = fields.Str(metadata={"description": "Path is the path to the copy of the file."})


class SandboxSchema(Schema):
    """Sandbox Schema"""

    _id = fields.Str(metadata={"description": "Unique scan identifier."})
    collections = fields.List(
        fields.Str(), metadata={"description": "List of connection events detected during this scan."}
    )
    connection = fields.List(
        fields.Nested(ConnectionSandboxSchema),
        metadata={"description": "List of connection events detected during this scan."},
    )
    dns = fields.List(
        fields.Nested(DNSSandboxSchema),
        metadata={"description": "List of DNS queries detected during this scan."},
    )
    entrypoint = fields.Str(metadata={"description": "Entrypoint is the command executed in the sandbox scan."})
    filesystem = fields.List(
        fields.Nested(FilesystemSandboxSchema),
        metadata={"description": "List of filesystem events detected during this scan."},
    )
    findings = fields.List(
        fields.Nested(FindingSandboxSchema), metadata={"description": "Findings from the sandbox scan."}
    )
    image = fields.Dict(metadata={"description": "Details of the image used in the sandbox scan."})
    image_name = fields.Str(
        data_key="imageName", metadata={"description": "ImageName is the image name (e.g. registry/repo:tag)."}
    )
    listening = fields.List(
        fields.Nested(ListeningSandboxSchema),
        metadata={"description": "Listening is a list of listening events detected during this scan."},
    )
    _pass = fields.Bool(data_key="pass", metadata={"description": "Pass indicates if the scan passed or failed."})
    procs = fields.List(
        fields.Nested(ProcsSandboxSchema),
        metadata={"description": "Procs are the different detected process during this scan."},
    )
    risk_score = fields.Float(
        data_key="riskScore", metadata={"description": "RiskScore is the weighted total risk score."}
    )
    scan_duration = fields.Int(
        data_key="scanDuration", metadata={"description": "ScanDuration is the provided scan duration in nanoseconds."}
    )
    scan_time = PCCEDateTime(data_key="scanTime", metadata={"description": "Start is the scan start time."})
    suspicious_files = fields.List(
        fields.Nested(SuspiciousFileSandboxSchema),
        data_key="suspiciousFiles",
        metadata={"description": "SuspiciousFiles are suspicious files detected during scan."},
    )
