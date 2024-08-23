from __future__ import annotations

import responses

USER = {
    "authType": "saml",
    "lastModified": "2024-07-22T20:11:39.333Z",
    "password": "string",
    "permissions": [{"collections": ["string"], "project": "string"}],
    "role": "string",
    "username": "string",
}


@responses.activate
def test_users_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/users", json=[USER for i in range(10)])
    resp = pcce.users.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == USER


@responses.activate
def test_users_create(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/users")
    pcce.users.create(data=USER)


@responses.activate
def test_users_update(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/users")
    pcce.users.update(data=USER)


@responses.activate
def test_users_update_password(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/users/password")
    pcce.users.update_password(old_password="password", new_password="password")


@responses.activate
def test_users_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/users/user1")
    pcce.users.delete(username="user1")
