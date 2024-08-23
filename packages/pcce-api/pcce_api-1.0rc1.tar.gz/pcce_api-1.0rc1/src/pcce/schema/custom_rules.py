from __future__ import annotations

from marshmallow import Schema, fields, validate


class CustomRuleSchema(Schema):
    _id = fields.Int(metadata={"description": "Rule ID. Must be unique."})
    attack_techniques = fields.List(
        fields.Str(
            validate=validate.OneOf(
                [
                    "exploitationForPrivilegeEscalation",
                    "exploitPublicFacingApplication",
                    "applicationExploitRCE",
                    "networkServiceScanning",
                    "endpointDenialOfService",
                    "exfiltrationGeneral",
                    "systemNetworkConfigurationDiscovery",
                    "unsecuredCredentials",
                    "credentialDumping",
                    "systemInformationDiscovery",
                    "systemNetworkConnectionDiscovery",
                    "systemUserDiscovery",
                    "accountDiscovery",
                    "cloudInstanceMetadataAPI",
                    "accessKubeletMainAPI",
                    "queryKubeletReadonlyAPI",
                    "accessKubernetesAPIServer",
                    "softwareDeploymentTools",
                    "ingressToolTransfer",
                    "lateralToolTransfer",
                    "commandAndControlGeneral",
                    "resourceHijacking",
                    "manInTheMiddle",
                    "nativeBinaryExecution",
                    "foreignBinaryExecution",
                    "createAccount",
                    "accountManipulation",
                    "abuseElevationControlMechanisms",
                    "supplyChainCompromise",
                    "obfuscatedFiles",
                    "hijackExecutionFlow",
                    "impairDefences",
                    "scheduledTaskJob",
                    "exploitationOfRemoteServices",
                    "eventTriggeredExecution",
                    "accountAccessRemoval",
                    "privilegedContainer",
                    "writableVolumes",
                    "execIntoContainer",
                    "softwareDiscovery",
                    "createContainer",
                    "kubernetesSecrets",
                    "fileAndDirectoryDiscovery",
                    "masquerading",
                    "webShell",
                    "compileAfterDelivery",
                ]
            )
        ),
        data_key="attackTechniques",
        metadata={"description": "List of attack techniques."},
    )
    description = fields.Str(metadata={"description": "Description of the rule."})
    message = fields.Str(metadata={"description": "Macro that is printed as part of the audit/incident message."})
    min_version = fields.Str(
        data_key="minVersion", metadata={"description": "Minimum version required to support the rule."}
    )
    modified = fields.Int(metadata={"description": "Datetime when the rule was created or last modified."})
    name = fields.Str(metadata={"description": "Name of the rule."})
    owner = fields.Str(metadata={"description": "User who created or modified the rule."})
    script = fields.Str(metadata={"description": "Custom script."})
    _type = fields.Str(
        data_key="type",
        validate=validate.OneOf(
            ["processes", "filesystem", "network-outgoing", "kubernetes-audit", "waas-request", "waas-response"]
        ),
        metadata={"description": "Type is the type of the custom rule."},
    )
    vuln_ids = fields.List(fields.Str(), data_key="vulnIDs", metadata={"description": "List of vulnerability IDs."})
