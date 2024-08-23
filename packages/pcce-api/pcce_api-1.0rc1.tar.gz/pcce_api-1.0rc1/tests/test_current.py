from __future__ import annotations

import responses

COLLECTION = {"color": "string", "name": "string"}
PROJECT = {"_id": "string", "address": "string", "connected": True, "creationTime": "2024-07-12T09:46:19.416Z"}


@responses.activate
def test_current_list_collections(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/current/collections", json=[COLLECTION for i in range(10)]
    )
    resp = pcce.current.list_collections()
    assert isinstance(resp, list)
    for item in resp:
        assert item == COLLECTION


@responses.activate
def test_current_list_projects(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/current/projects", json=[PROJECT for i in range(10)])
    resp = pcce.current.list_projects()
    assert isinstance(resp, list)
    for item in resp:
        assert item == PROJECT
