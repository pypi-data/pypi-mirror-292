from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_serverless_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/serverless", json=[{"key": "value"} for i in range(10)])
    resp = pcce.serverless.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_serverless_download(pcce):
    fobj = BytesIO(b"Test file content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/serverless/download", body=fobj.read())
    fobj.seek(0)
    resp = pcce.serverless.download()
    assert resp.read() == fobj.read()


@responses.activate
def test_serverless_resolve(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/serverless/evaluate")
    pcce.serverless.resolve(data={"key": "value"})


@responses.activate
def test_serverless_names(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/serverless/names", json=["names" for i in range(10)])
    resp = pcce.serverless.names()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "names"


@responses.activate
def test_serverless_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/serverless/scan")
    pcce.serverless.scan()


@responses.activate
def test_serverless_stop(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/serverless/stop")
    pcce.serverless.stop()
