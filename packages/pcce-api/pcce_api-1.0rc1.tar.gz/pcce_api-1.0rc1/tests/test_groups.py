from __future__ import annotations

import responses

GROUP = {
    "_id": "string",
    "groupId": "string",
    "groupName": "string",
    "lastModified": "2024-07-22T20:11:38.911Z",
    "ldapGroup": True,
    "oauthGroup": True,
    "oidcGroup": True,
    "owner": "string",
    "permissions": [{"collections": ["string"], "project": "string"}],
    "role": "string",
    "samlGroup": True,
    "user": [{"username": "string"}],
}


@responses.activate
def test_groups_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/groups", json=[GROUP for i in range(10)])
    resp = pcce.groups.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == GROUP


@responses.activate
def test_groups_list_names(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/groups/names", json=["string" for i in range(10)])
    resp = pcce.groups.list_names()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "string"


@responses.activate
def test_groups_create(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/groups")
    pcce.groups.create(data=GROUP)


@responses.activate
def test_groups_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/groups/group1")
    pcce.groups.delete(_id="group1")


@responses.activate
def test_groups_update(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/groups/group1")
    pcce.groups.update(_id="group1", data=GROUP)
