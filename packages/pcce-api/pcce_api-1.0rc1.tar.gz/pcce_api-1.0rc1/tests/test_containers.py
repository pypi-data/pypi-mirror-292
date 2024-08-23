from __future__ import annotations

from io import BytesIO

import responses

CONTAINER_RESULT = {
    "_id": "string",
    "agentless": True,
    "agentlessScanID": 0,
    "collections": ["string"],
    "csa": True,
    "runtimeEnabled": True,
    "scanTime": "2024-07-12T09:46:19.409Z",
}


@responses.activate
def test_containers_list_scan_result(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/containers", json=[CONTAINER_RESULT for i in range(10)])
    resp = pcce.containers.list_scan_result()
    assert isinstance(resp, list)
    for item in resp:
        assert item == CONTAINER_RESULT


@responses.activate
def test_containers_get_count(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/containers/count", json=1)
    resp = pcce.containers.get_count()
    assert resp == 1


@responses.activate
def test_containers_download_scan_result(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/containers/download",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.containers.download_scan_result()
    assert test_file.read() == fobj.read()


@responses.activate
def test_containers_list_name(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/containers/names", json=["string" for i in range(10)])
    resp = pcce.containers.list_name()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "string"


@responses.activate
def test_containers_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/containers/scan")
    pcce.containers.scan()
