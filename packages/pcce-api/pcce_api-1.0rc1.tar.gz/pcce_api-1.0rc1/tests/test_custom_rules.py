from __future__ import annotations

import responses

CUSTOM_RULE = {
    "_id": 0,
    "attackTechniques": [
        "exploitationForPrivilegeEscalation",
    ],
    "description": "string",
    "message": "string",
    "minVersion": "string",
    "modified": 0,
    "name": "string",
    "owner": "string",
    "script": "string",
    "type": "processes",
    "vulnIDs": ["string"],
}


@responses.activate
def test_custom_rules_list(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/custom-rules",
        json=[CUSTOM_RULE for i in range(10)],
    )
    resp = pcce.custom_rules.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == CUSTOM_RULE


@responses.activate
def test_custom_rules_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/custom-rules/0")
    pcce.custom_rules.delete(_id=0)


@responses.activate
def test_custom_rules_update(pcce):
    responses.add(
        responses.PUT,
        "https://localhost:8083/api/v1/custom-rules/0",
        json=CUSTOM_RULE,
    )
    pcce.custom_rules.update(data=CUSTOM_RULE)
