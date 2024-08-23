from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_agentless_progress(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/agentless/progress")
    pcce.agentless.progress()


@responses.activate
def test_agentless_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/agentless/scan")
    pcce.agentless.scan()


@responses.activate
def test_agentless_stop(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/agentless/stop")
    pcce.agentless.stop()


@responses.activate
def test_agentless_templates(pcce):
    fobj = BytesIO(b"Test content")
    responses.add(responses.POST, "https://localhost:8083/api/v1/agentless/templates", body=fobj.read())
    fobj.seek(0)
    resp = pcce.agentless.templates(
        data={
            "awsRegionType": "all",
            "credential": {
                "_id": "string",
                "accountGUID": "string",
                "accountID": "string",
                "accountName": "string",
                "apiToken": {"encrypted": "string", "plain": "string"},
                "azureSPInfo": {
                    "clientId": "string",
                    "miType": "user-assigned",
                    "subscriptionId": "string",
                    "tenantId": "string",
                },
                "caCert": "string",
                "cloudProviderAccountID": "string",
                "created": "2024-07-23T18:19:08.218Z",
                "description": "string",
                "external": True,
                "global": True,
                "lastModified": "2024-07-23T18:19:08.218Z",
                "ociCred": {"fingerprint": "string", "tenancyId": "string"},
                "owner": "string",
                "prismaLastModified": 0,
                "roleArn": "string",
                "secret": {"encrypted": "string", "plain": "string"},
                "skipVerify": True,
                "stsEndpoints": ["string"],
                "tokens": {
                    "awsAccessKeyId": "string",
                    "awsSecretAccessKey": {"encrypted": "string", "plain": "string"},
                    "duration": 0,
                    "expirationTime": "2024-07-23T18:19:08.218Z",
                    "token": {"encrypted": "string", "plain": "string"},
                },
                "type": "aws",
                "url": "string",
                "useAWSRole": True,
                "useSTSRegionalEndpoint": True,
            },
            "credentialID": "string",
        }
    )
    assert resp.read() == fobj.read()
