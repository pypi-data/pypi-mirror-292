"""
Audits Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields

from .utils import PCCEDateTime


class DockerAccessParamsSchema(Schema):
    """Docker Access Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audit."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audit."}
    )
    _type = fields.Str(data_key="type", metadata={"description": "Type is the audit type."})
    rule_name = fields.List(
        fields.Str(), data_key="ruleName", metadata={"description": "RuleNames are the rules names to filter by."}
    )
    api = fields.List(fields.Str(), metadata={"description": "APIs are apis to filter by."})
    hostname = fields.List(fields.Str(), metadata={"description": "Hosts are hosts to filter by."})
    user = fields.List(fields.Str(), metadata={"description": "Users are users to filter by."})
    allow = fields.Str(metadata={"description": "Allow indicated whether allowed requests should be shown."})
    cluster = fields.List(fields.Str(), metadata={"description": "Clusters is the cluster filter."})


class AdmissionParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the activity."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the activity."}
    )
    namespace = fields.List(
        fields.Str(), metadata={"description": "Namespaces is the list of namespaces to use for filtering."}
    )
    operation = fields.List(
        fields.Str(), metadata={"description": "Operations is the list of operations to use for filtering."}
    )
    cluster = fields.List(fields.Str(), metadata={"description": "Clusters is the cluster filter."})
    attack_techniques = fields.List(
        fields.Str(),
        data_key="attackTechniques",
        metadata={"description": "AttackTechniques are the MITRE attack techniques."},
    )


class WAASParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audit."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audit."}
    )
    image_name = fields.List(
        fields.Str(), data_key="imageName", metadata={"description": "Images is the image names filter."}
    )
    container_name = fields.List(
        fields.Str(), data_key="containerName", metadata={"description": "Containers is the container names filter."}
    )
    hostname = fields.List(fields.Str(), metadata={"description": "Hosts is the hostnames filter."})
    rule_name = fields.List(
        fields.Str(), data_key="ruleName", metadata={"description": "RuleNames is the rule names filter."}
    )
    _type = fields.List(
        fields.Str(), data_key="type", metadata={"description": "Types is the firewall audit type filter."}
    )
    effect = fields.Str(metadata={"description": "Effect is used to filter by runtime audit effect."})
    rule_app_id = fields.List(
        fields.Str(), data_key="ruleAppId", metadata={"description": "RuleAppIDs is the rule app IDs filter."}
    )
    function = fields.List(fields.Str(), metadata={"description": "FunctionName is used to filter by function name."})
    runtime = fields.List(fields.Str(), metadata={"description": "Runtime is used to filter by runtime."})
    ns = fields.List(
        fields.Str(), metadata={"description": "Namespaces is the list of namespaces to use for filtering."}
    )
    app_id = fields.List(
        fields.Str(), data_key="appID", metadata={"description": "AppIDs is the app embedded appID filter."}
    )
    subnet = fields.List(fields.Str(), metadata={"description": "Subnets is the source IPs filter."})
    connecting_ips = fields.List(
        fields.Str(), data_key="connectingIPs", metadata={"description": "ConnectingIPs is the connecting IPs filter."}
    )
    country = fields.List(fields.Str(), metadata={"description": "Countries is the source IP country filter."})
    user_agent_header = fields.List(
        fields.Str(),
        data_key="userAgentHeader",
        metadata={"description": "UserAgents is the user agent header filter."},
    )
    url = fields.List(fields.Str(), metadata={"description": "URLs is the URL filter."})
    request_host = fields.List(
        fields.Str(), data_key="requestHost", metadata={"description": "RequestHosts is the request host filter."}
    )
    url_path = fields.List(fields.Str(), data_key="urlPath", metadata={"description": "Paths is the URL path filter."})
    url_query = fields.List(
        fields.Str(), data_key="urlQuery", metadata={"description": "Queries is the URL query filter."}
    )
    method = fields.List(fields.Str(), metadata={"description": "Methods is the request method filter."})
    request_header_names = fields.List(
        fields.Str(),
        data_key="requestHeaderNames",
        metadata={"description": "RequestHeaderNames is the request header names filter."},
    )
    os = fields.List(fields.Str(), metadata={"description": "OS is the OS filter."})
    msg = fields.List(fields.Str(), metadata={"description": "Messages is the audit message text filter."})
    cluster = fields.List(fields.Str(), metadata={"description": "Cluster is the audit cluster filter."})
    attack_techniques = fields.List(
        fields.Str(),
        data_key="attackTechniques",
        metadata={"description": "AttackTechniques are the MITRE attack techniques."},
    )
    aggregate = fields.Bool(
        metadata={
            "description": "Aggregate indicates whether the result audits should be aggregated according to the"
            "Select field."
        }
    )
    protection = fields.List(
        fields.Str(), metadata={"description": "Protections is the firewall audit protection type filter."}
    )
    event_id = fields.List(
        fields.Str(), data_key="eventID", metadata={"description": "EventID is the event IDs filter."}
    )
    owasp_top10 = fields.List(
        fields.Str(), data_key="owaspTop10", metadata={"description": "OWASPTop10 is the OWASP top 10 filter."}
    )
    owasp_api_top10 = fields.List(
        fields.Str(),
        data_key="owaspAPITop10",
        metadata={"description": "OWASPAPITop10 is the OWASP API top 10 filter."},
    )


class WAASTimeframeParamsSchema(WAASParamsSchema):
    buckets = fields.Int(metadata={"description": "Buckets is the number of buckets to return."})


class CNNSHostParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audits."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audits."}
    )
    src_image_name = fields.List(
        fields.Str(), data_key="srcImageName", metadata={"description": "SrcImages are the source images filter."}
    )
    dst_image_name = fields.List(
        fields.Str(), data_key="dstImageName", metadata={"description": "DstImages are the destination images filter."}
    )


class CNNSContainerParamsSchema(CNNSHostParamsSchema):
    block = fields.Str(metadata={"description": "Block is the block/audit filter."})


class IncidentParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audits."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audits."}
    )
    hostname = fields.List(
        fields.Str(), metadata={"description": "Filters results by hostname where the incident occurred."}
    )
    category = fields.List(fields.Str(), metadata={"description": "Filters results by incident category."})
    _type = fields.List(fields.Str(), data_key="type", metadata={"description": "Filters results by incident type."})
    profile_id = fields.List(
        fields.Str(), data_key="profileID", metadata={"description": "Filters results by runtime profile ID."}
    )
    acknowledged = fields.Str(metadata={"description": "Filters results by incidents that have been acknowledged."})
    cluster = fields.List(
        fields.Str(),
        metadata={"description": "Filters results by region (for functions) Filters results by cluster name."},
    )
    _id = fields.List(fields.Str(), data_key="id", metadata={"description": "Filters results by ID."})
    app_id = fields.List(fields.Str(), data_key="appID", metadata={"description": "Filters results by app IDs."})
    container_id = fields.List(
        fields.Str(), data_key="containerID", metadata={"description": "Filters results by container IDs."}
    )
    function_id = fields.List(
        fields.Str(), data_key="functionID", metadata={"description": "Filters results by function IDs."}
    )
    custom_rule_name = fields.List(
        fields.Str(), data_key="customRuleName", metadata={"description": "Filters results by custom rule names."}
    )


class KubernetesParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the activity."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the activity."}
    )
    user = fields.List(fields.Str(), metadata={"description": "Users is the list of users to use for filtering."})
    attack_techniques = fields.List(
        fields.Str(),
        data_key="attackTechniques",
        metadata={"description": "AttackTechniques are the MITRE attack techniques."},
    )
    cluster = fields.List(fields.Str(), metadata={"description": "Clusters is the list of clusters for filtering."})


class ManagementParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the activity."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the activity."}
    )
    _type = fields.List(fields.Str(), metadata={"description": "Types is the audit type filter."})
    username = fields.List(fields.Str(), metadata={"description": "Usernames is the username filter."})


class RuntimeParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _id = fields.List(fields.Str(), data_key="id", metadata={"description": "IDs are the audit IDs to filter."})
    profile_id = fields.List(
        fields.Str(), data_key="profileID", metadata={"description": "ProfileIDs are the profile IDs to filter."}
    )
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audit."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audit."}
    )
    time = PCCEDateTime(metadata={"description": "Time is used to filter by audit time."})
    image_name = fields.List(
        fields.Str(), data_key="imageName", metadata={"description": "ImageNames is the image name filter."}
    )
    container = fields.List(fields.Str(), metadata={"description": "Containers is the container name filter."})
    container_id = fields.List(
        fields.Str(), data_key="containerID", metadata={"description": "ContainerID is used to filter by container ID."}
    )
    rule_name = fields.List(
        fields.Str(), data_key="ruleName", metadata={"description": "RuleNames is used to filter by rule name."}
    )
    _type = fields.List(
        fields.Str(), data_key="type", metadata={"description": "Types is used to filter by runtime audit type."}
    )
    effect = fields.List(
        fields.Str(), metadata={"description": "Effect is used to filter by runtime audit effect (e.g., block/alert)."}
    )
    user = fields.List(fields.Str(), metadata={"description": "Users is used to filter by host users."})
    os = fields.List(fields.Str(), metadata={"description": "OS is the image OS distro filter."})
    namespace = fields.List(fields.Str(), metadata={"description": "Namespaces is the namespaces filter."})
    _fields = fields.List(
        fields.Str(),
        data_key="fields",
        metadata={"description": "Fields is used to fetch specific runtime audit fields."},
    )
    cluster = fields.List(fields.Str(), metadata={"description": "Clusters is the cluster filter."})
    attack_type = fields.List(
        fields.Str(),
        data_key="attackType",
        metadata={"description": "AttackTypes is used to filter by runtime audit attack type."},
    )
    hostname = fields.List(fields.Str(), metadata={"description": "Hostname is the hostname filter."})
    msg = fields.List(fields.Str(), metadata={"description": "Message is the audit message text filter."})
    interactive = fields.List(fields.Str(), metadata={"description": "Interactive is the audit interactive filter."})
    function = fields.List(fields.Str(), metadata={"description": "Function is used to filter by function name."})
    runtime = fields.List(fields.Str(), metadata={"description": "Runtime is used to filter by runtime."})
    attack_techniques = fields.List(
        fields.Str(),
        data_key="attackTechniques",
        metadata={"description": "AttackTechniques are the MITRE attack techniques."},
    )
    app = fields.List(
        fields.Str(), metadata={"description": "App is the name constraint of the service that triggered the audit."}
    )
    process_path = fields.List(
        fields.Str(),
        data_key="processPath",
        metadata={"description": "ProcessPath is the path constraint of the process that triggered the audit."},
    )
    request_id = fields.List(
        fields.Str(), data_key="requestID", metadata={"description": "RequestID is used to filter by request ID."}
    )
    function_id = fields.List(
        fields.Str(), data_key="functionID", metadata={"description": "FunctionID is used to filter by function ID."}
    )
    aggregate = fields.Bool(
        metadata={
            "description": "Aggregate indicates whether the result audits should be aggregated according to the "
            "Select field."
        }
    )
    app_id = fields.List(
        fields.Str(),
        data_key="appID",
        metadata={"description": "AppID is used to filter by embedded app or Fargate task that triggered the audit."},
    )


class RuntimeTimeframeParamsSchema(RuntimeParamsSchema):
    block = fields.Str(metadata={"description": "Block is the block/audit filter."})


class RuntimeFileIntegrityParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _id = fields.List(fields.Str(), data_key="id", metadata={"description": "IDs are the audit IDs to filter."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audit."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audit."}
    )
    hostname = fields.List(fields.Str(), metadata={"description": "Hosts is the list of hosts to use for filtering."})
    path = fields.List(fields.Str(), metadata={"description": "Paths is the list of paths to use for filtering."})
    event_type = fields.List(
        fields.Str(),
        data_key="eventType",
        metadata={"description": "EventTypes is the list of file integrity events to use for filtering."},
    )
    cluster = fields.List(fields.Str(), metadata={"description": "Clusters is the cluster filter."})


class RuntimeLogInspectionParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _id = fields.List(
        fields.Str(), data_key="id", metadata={"description": "IDs is the list of IDs to use for filtering."}
    )
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the events."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the events."}
    )
    hostname = fields.List(fields.Str(), metadata={"description": "Hosts is the list of hosts to use for filtering."})
    logfile = fields.List(
        fields.Str(), metadata={"description": "Logfiles is the list of log files to use for filtering."}
    )
    cluster = fields.List(fields.Str(), metadata={"description": "Clusters is the cluster filter."})


class RuntimeServerlessParamsSchema(Schema):
    """
    Schema for runtime serverless events.
    """

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    profile_id = fields.List(
        fields.Str(), data_key="profileID", metadata={"description": "ProfileIDs are the profile IDs to filter."}
    )
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audit."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audit."}
    )
    time = fields.DateTime(metadata={"description": "Time is used to filter by audit time."})
    rule_name = fields.List(
        fields.Str(), data_key="ruleName", metadata={"description": "RuleNames is used to filter by rule name."}
    )
    _type = fields.List(
        fields.Str(), data_key="type", metadata={"description": "Types is used to filter by runtime audit type."}
    )
    effect = fields.List(
        fields.Str(),
        metadata={"description": "Effect is used to filter by runtime audit effect (e.g., block/alert)."},
    )
    function = fields.List(fields.Str(), metadata={"description": "Function is used to filter by function name."})
    runtime = fields.List(fields.Str(), metadata={"description": "Runtime is used to filter by runtime."})
    attack_techniques = fields.List(
        fields.Str(),
        data_key="attackTechniques",
        metadata={"description": "AttackTechniques are the MITRE attack techniques."},
    )
    request_id = fields.List(
        fields.Str(), data_key="requestID", metadata={"description": "RequestID is used to filter by request ID."}
    )
    msg = fields.List(fields.Str(), metadata={"description": "Message is the audit message text filter."})
    attack_type = fields.List(
        fields.Str(),
        data_key="attackType",
        metadata={"description": "AttackTypes is used to filter by runtime audit attack type."},
    )
    aggregate = fields.Bool(
        metadata={
            "description": "Aggregate indicates whether the result audits should be aggregated according to the"
            "Select field."
        },
    )


class RuntimeServerlessTimeframeParamsSchema(RuntimeServerlessParamsSchema):
    block = fields.Str(metadata={"description": "Block is the block/audit filter."})


class TrustParamsSchema(Schema):
    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audit."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audit."}
    )
    rule_name = fields.List(
        fields.Str(), data_key="ruleName", metadata={"description": "RuleNames is used to filter by rule name."}
    )
    effect = fields.List(
        fields.Str(),
        metadata={"description": "Effect is used to filter by runtime audit effect (e.g., block/alert)."},
    )
    _id = fields.Str(metadata={"description": "IDs is used to filter by registry/repo."})
