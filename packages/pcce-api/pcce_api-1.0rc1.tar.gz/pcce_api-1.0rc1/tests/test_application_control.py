from __future__ import annotations

import responses

HOST_APP_CONTROL_RULE = {
    "_id": 0,
    "applications": [{"allowedVersions": ["string"], "name": "string"}],
    "description": "string",
    "disabled": True,
    "modified": "2024-07-03T15:11:19.250Z",
    "name": "string",
    "notes": "string",
    "owner": "string",
    "previousName": "string",
    "severity": "string",
}


@responses.activate
def test_application_control_list(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/application-control/host",
        json=[HOST_APP_CONTROL_RULE for _ in range(20)],
    )
    resp = pcce.application_control.list()
    assert isinstance(resp, list)
    for item in resp:
        assert HOST_APP_CONTROL_RULE == item


@responses.activate
def test_application_control_upsert(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/application-control/host", json=HOST_APP_CONTROL_RULE)
    resp = pcce.application_control.upsert(HOST_APP_CONTROL_RULE)
    assert resp == HOST_APP_CONTROL_RULE


@responses.activate
def test_application_control_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/application-control/host/1")
    pcce.application_control.delete(1)
