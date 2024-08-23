from __future__ import annotations

import responses

CUSTOM_COMPLIANCE = {
    "_id": 0,
    "disabled": True,
    "modified": "2024-07-12T09:46:19.416Z",
    "name": "string",
    "notes": "string",
    "owner": "string",
    "previousName": "string",
    "script": "string",
    "severity": "string",
    "title": "string",
}


@responses.activate
def test_custom_compliance_list(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/custom-compliance",
        json=[CUSTOM_COMPLIANCE for i in range(10)],
    )
    resp = pcce.custom_compliance.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == CUSTOM_COMPLIANCE


@responses.activate
def test_custom_compliance_update(pcce):
    responses.add(
        responses.PUT,
        "https://localhost:8083/api/v1/custom-compliance",
        json=CUSTOM_COMPLIANCE,
    )
    resp = pcce.custom_compliance.update(data=CUSTOM_COMPLIANCE)
    assert resp == CUSTOM_COMPLIANCE


@responses.activate
def test_custom_compliance_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/custom-compliance/0")
    pcce.custom_compliance.delete(id="0")
