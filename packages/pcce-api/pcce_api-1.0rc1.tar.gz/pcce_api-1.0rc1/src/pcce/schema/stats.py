"""
Stats Schema
"""

from __future__ import annotations

from marshmallow import Schema, fields, validate

from .utils import PCCEDateTime


class ComplianceStatParamsSchema(Schema):
    """Compliance Stat Params Schema"""

    collections = fields.List(
        fields.Str(),
        metadata={"description": "Scopes query by collection."},
    )
    account_ids = fields.List(
        fields.Str(),
        data_key="accountIDs",
        metadata={"description": "Scopes query by account ID."},
    )
    rule_name = fields.Str(data_key="ruleName", metadata={"description": "Filters results by rule name."})
    policy_type = fields.Str(
        data_key="policyType",
        validate=validate.OneOf(
            [
                "containerVulnerability",
                "containerCompliance",
                "ciImagesVulnerability",
                "ciImagesCompliance",
                "hostVulnerability",
                "hostCompliance",
                "vmVulnerability",
                "vmCompliance",
                "serverlessCompliance",
                "ciServerlessCompliance",
                "serverlessVulnerability",
                "ciServerlessVulnerability",
                "containerRuntime",
                "appEmbeddedRuntime",
                "containerAppFirewall",
                "hostAppFirewall",
                "outOfBandAppFirewall",
                "agentlessAppFirewall",
                "appEmbeddedAppFirewall",
                "serverlessAppFirewall",
                "networkFirewall",
                "secrets",
                "hostRuntime",
                "serverlessRuntime",
                "kubernetesAudit",
                "trust",
                "admission",
                "codeRepoVulnerability",
                "ciCodeRepoVulnerability",
                "codeRepoCompliance",
                "ciCodeRepoCompliance",
            ]
        ),
        metadata={
            "description": "Filters results by policy type. Used to further scope queries because rule names do not"
            "need to be unique between policies."
        },
    )
    category = fields.Str(
        validate=validate.OneOf(
            [
                "Docker",
                "Docker (DISA STIG)",
                "Twistlock Labs",
                "Custom",
                "Istio",
                "Linux",
                "Kubernetes",
                "CRI",
                "OpenShift",
                "Application Control",
                "GKE",
                "Prisma Cloud Labs",
                "EKS",
            ]
        ),
        metadata={"description": "Filters results by category. For example, a benchmark or resource type."},
    )
    template = fields.Str(
        validate=validate.OneOf(["PCI", "HIPAA", "NIST SP 800-190", "GDPR", "DISA STIG"]),
        metadata={"description": "Filters results by compliance template."},
    )


class EventStatParamsSchema(Schema):
    """Event Stat Params Schema"""

    collections = fields.List(
        fields.Str(),
        metadata={"description": "Scopes query by collection."},
    )
    account_ids = fields.List(
        fields.Str(),
        data_key="accountIDs",
        metadata={"description": "Scopes query by account ID."},
    )
    _from = PCCEDateTime(
        data_key="from", metadata={"description": "From is an optional minimum time constraints for the audit."}
    )
    _to = PCCEDateTime(
        data_key="to", metadata={"description": "To is an optional maximum time constraints for the audit."}
    )
    attack_techniques = fields.List(
        fields.Str(),
        data_key="attackTechniques",
        metadata={"description": "AttackTechniques are the MITRE attack techniques."},
    )


class VulnStatParamsSchema(Schema):
    """Vuln Stat Params Schema"""

    offset = fields.Int(
        metadata={"description": "Offsets the result to a specific report count. Offset starts from 0."}
    )
    limit = fields.Int(metadata={"description": "Limit is the amount to fix."})
    sort = fields.Str(metadata={"description": "Sorts the result using a key."})
    reverse = fields.Bool(metadata={"description": "Sorts the result in reverse order."})
    cve = fields.Str(metadata={"description": "CVE is the single CVE ID to return vulnerability data for."})
    severity_threshold = fields.Str(
        data_key="severityThreshold",
        metadata={
            "description": "SeverityThreshold is the minimum severity indicating that all retrieved CVEs severities are"
            "greater than or equal to the threshold."
        },
    )
    cvss_threshold = fields.Str(
        data_key="cvssThreshold",
        metadata={
            "description": "CVSSThreshold is the minimum CVSS score indicating that all retrieved CVEs CVSS scores are"
            "greater than or equal to the threshold."
        },
    )
    resource_type = fields.Str(
        data_key="resourceType",
        validate=validate.OneOf(["container", "image", "host", "istio", "vm", "function", "codeRepo", "registryImage"]),
        metadata={"description": "ResourceType is the single resource type to return vulnerability data for."},
    )
    agentless = fields.Bool(metadata={"description": "Agentless is the agentless filter."})
    stopped = fields.Bool(
        metadata={
            "description": "Stopped indicates whether to retrieve vulnerability data for hosts that were not running"
            "during agentless scan."
        }
    )
    packages = fields.List(fields.Str(), metadata={"description": "Packages filter by impacted packages."})
    risk_factors = fields.List(
        fields.Str(), data_key="riskFactors", metadata={"description": "RiskFactors filter by CVE risk factors."}
    )
    env_risk_factors = fields.List(
        fields.Str(),
        data_key="envRiskFactors",
        metadata={"description": "EnvRiskFactors filter by environmental risk factors."},
    )
