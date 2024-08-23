from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_vms_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/vms", json=[{"key": "value"} for i in range(10)])
    resp = pcce.vms.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_vms_download(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/vms/download", body=fobj.read())
    fobj.seek(0)
    resp = pcce.vms.download()
    assert resp.read() == fobj.read()


@responses.activate
def test_vms_tags(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/vms/labels", json=[{"key": "value"} for i in range(10)])
    resp = pcce.vms.tags()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_vms_names(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/vms/names", json=["names" for i in range(10)])
    resp = pcce.vms.names()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "names"


@responses.activate
def test_vms_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/vms/scan")
    pcce.vms.scan()


@responses.activate
def test_vms_stop(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/vms/stop")
    pcce.vms.stop()
