from __future__ import annotations

import responses

SANDBOX = {
    "_id": "string",
    "collections": ["string"],
    "connection": [
        {
            "countryCode": "string",
            "ip": "string",
            "port": 0,
            "process": {
                "command": "string",
                "md5": "string",
                "parent": {
                    "command": "string",
                    "md5": "string",
                    "path": "string",
                    "time": "2024-08-02T20:22:08.677Z",
                    "user": "string",
                },
                "path": "string",
                "time": "2024-08-02T20:22:08.677Z",
                "user": "string",
            },
            "protocol": "string",
            "time": "2024-08-02T20:22:08.677Z",
        }
    ],
    "dns": [
        {
            "countryCode": "string",
            "domainName": "string",
            "domainType": "string",
            "ip": "string",
            "process": {
                "command": "string",
                "md5": "string",
                "parent": {
                    "command": "string",
                    "md5": "string",
                    "path": "string",
                    "time": "2024-08-02T20:22:08.677Z",
                    "user": "string",
                },
                "path": "string",
                "time": "2024-08-02T20:22:08.677Z",
                "user": "string",
            },
            "time": "2024-08-02T20:22:08.677Z",
        }
    ],
    "entrypoint": "string",
    "filesystem": [
        {
            "accessType": "open",
            "path": "string",
            "process": {
                "command": "string",
                "md5": "string",
                "parent": {
                    "command": "string",
                    "md5": "string",
                    "path": "string",
                    "time": "2024-08-02T20:22:08.677Z",
                    "user": "string",
                },
                "path": "string",
                "time": "2024-08-02T20:22:08.677Z",
                "user": "string",
            },
            "time": "2024-08-02T20:22:08.677Z",
        }
    ],
    "findings": [
        {
            "description": "string",
            "events": [{"description": "string", "time": "2024-08-02T20:22:08.677Z"}],
            "severity": "critical",
            "time": "2024-08-02T20:22:08.677Z",
            "type": "filelessExecution",
        }
    ],
    "imageName": "string",
    "listening": [
        {
            "port": 0,
            "process": {
                "command": "string",
                "md5": "string",
                "parent": {
                    "command": "string",
                    "md5": "string",
                    "path": "string",
                    "time": "2024-08-02T20:22:08.680Z",
                    "user": "string",
                },
                "path": "string",
                "time": "2024-08-02T20:22:08.680Z",
                "user": "string",
            },
            "time": "2024-08-02T20:22:08.680Z",
        }
    ],
    "pass": True,
    "procs": [
        {
            "command": "string",
            "md5": "string",
            "parent": {
                "command": "string",
                "md5": "string",
                "path": "string",
                "time": "2024-08-02T20:22:08.680Z",
                "user": "string",
            },
            "path": "string",
            "time": "2024-08-02T20:22:08.680Z",
            "user": "string",
        }
    ],
    "riskScore": 0,
    "scanDuration": 0,
    "scanTime": "2024-08-02T20:22:08.680Z",
    "suspiciousFiles": [{"containerPath": "string", "created": True, "md5": "string", "path": "string"}],
}


@responses.activate
def test_sandbox_add(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/sandbox", json=SANDBOX)
    resp = pcce.sandbox.add(data=SANDBOX)
    assert resp == SANDBOX
