from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_tas_droplets_list(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/tas-droplets", json=[{"key": "value"} for i in range(10)]
    )
    resp = pcce.tas_droplets.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_tas_droplets_addresses(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/tas-droplets/addresses", json=["address" for i in range(10)]
    )
    resp = pcce.tas_droplets.addresses()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "address"


@responses.activate
def test_tas_droplets_download(pcce):
    fobj = BytesIO(b"test content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/tas-droplets/download", body=fobj.read())
    fobj.seek(0)
    resp = pcce.tas_droplets.download()
    assert resp.read() == fobj.read()


@responses.activate
def test_tas_droplets_progress(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/tas-droplets/progress", json={"key": "value"})
    resp = pcce.tas_droplets.progress()
    assert resp == {"key": "value"}


@responses.activate
def test_tas_droplets_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/tas-droplets/scan")
    pcce.tas_droplets.scan()


@responses.activate
def test_tas_droplets_stop(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/tas-droplets/stop")
    pcce.tas_droplets.stop()
