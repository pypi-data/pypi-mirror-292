from __future__ import annotations

import responses

COLLECTION = {
    "accountIDs": ["string"],
    "appIDs": ["string"],
    "clusters": ["string"],
    "codeRepos": ["string"],
    "color": "string",
    "containers": ["string"],
    "description": "string",
    "functions": ["string"],
    "hosts": ["string"],
    "images": ["string"],
    "labels": ["string"],
    "modified": "2024-07-12T09:46:19.403Z",
    "name": "string",
    "namespaces": ["string"],
    "owner": "string",
    "prisma": True,
    "system": True,
}


@responses.activate
def test_collections_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/collections", json=[COLLECTION for i in range(10)])
    resp = pcce.collections.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == COLLECTION


@responses.activate
def test_collections_create(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/collections")
    pcce.collections.create(data=COLLECTION)


@responses.activate
def test_collections_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/collections/my-collection")
    pcce.collections.delete(name="my-collection")


@responses.activate
def test_collections_update(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/collections/my-collection")
    pcce.collections.update(name="my-collection", data=COLLECTION)


@responses.activate
def test_collections_get_policy(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/collections/my-collection/usages")
    pcce.collections.get_policy(name="my-collection")
