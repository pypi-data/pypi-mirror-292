from __future__ import annotations

import responses

TAG = {
    "color": "string",
    "description": "string",
    "name": "string",
    "vulns": [
        {
            "checkBaseLayer": True,
            "comment": "string",
            "id": "string",
            "packageName": "string",
            "resourceType": "image",
            "resources": ["string"],
        }
    ],
}
VULNTAG = {"id": "CVE-2020-16156", "packageName": "*", "resourceType": "image", "resources": ["*"]}


@responses.activate
def test_tags_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/tags", json=[TAG for i in range(10)])
    resp = pcce.tags.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == TAG


@responses.activate
def test_tags_add(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/tags")
    pcce.tags.add(data=TAG)


@responses.activate
def test_tags_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/tags/string")
    pcce.tags.delete(_id="string")


@responses.activate
def test_tags_update(pcce):
    responses.add(responses.PUT, "https://localhost:8083/api/v1/tags/string")
    pcce.tags.update(_id="string", data=TAG)


@responses.activate
def test_tags_delete_vuln(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/tags/string/vuln")
    pcce.tags.delete_vuln(_id="string")


@responses.activate
def test_tags_set_vuln(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/tags/string/vuln")
    pcce.tags.set_vuln(_id="string", vuln_data=VULNTAG)
