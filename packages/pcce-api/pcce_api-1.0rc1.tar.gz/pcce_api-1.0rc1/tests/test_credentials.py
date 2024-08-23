from __future__ import annotations

import responses

CREDENTIAL = {
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
    "created": "2024-07-23T18:19:08.427Z",
    "description": "string",
    "external": True,
    "global": True,
    "lastModified": "2024-07-23T18:19:08.427Z",
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
        "expirationTime": "2024-07-23T18:19:08.427Z",
        "token": {"encrypted": "string", "plain": "string"},
    },
    "type": "aws",
    "url": "string",
    "useAWSRole": True,
    "useSTSRegionalEndpoint": True,
}
CREDENTIAL_USEAGE = {
    "description": "string",
    "type": "Alert settings",
}


@responses.activate
def test_credentials_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/credentials", json=[CREDENTIAL for i in range(10)])
    resp = pcce.credentials.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == CREDENTIAL


@responses.activate
def test_credentials_add(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/credentials")
    pcce.credentials.add(data=CREDENTIAL)


@responses.activate
def test_credentials_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/credentials/my-id")
    pcce.credentials.delete(_id="my-id")


@responses.activate
def test_credentials_get_usages(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/credentials/my-id/usages",
        json=[CREDENTIAL_USEAGE for i in range(10)],
    )
    resp = pcce.credentials.get_usages("my-id")
    assert isinstance(resp, list)
    for item in resp:
        assert item == CREDENTIAL_USEAGE
