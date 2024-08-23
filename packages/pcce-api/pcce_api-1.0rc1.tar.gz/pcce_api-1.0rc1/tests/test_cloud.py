from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_cloud_list_discovery_result(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/cloud/discovery",
        json=["EXAMPLE"],
    )
    resp = pcce.cloud.list_discovery_result()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "EXAMPLE"


@responses.activate
def test_cloud_download_discovery_result(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/cloud/discovery/download",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.cloud.download_discovery_result()
    assert test_file.read() == fobj.read()


@responses.activate
def test_cloud_list_discovery_entities(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/cloud/discovery/entities",
        json=["EXAMPLE"],
    )
    resp = pcce.cloud.list_discovery_entities()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "EXAMPLE"


@responses.activate
def test_cloud_scan_discovery(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/cloud/scan")
    pcce.cloud.scan_discovery()


@responses.activate
def test_cloud_stop_discovery(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/cloud/stop")
    pcce.cloud.stop_discovery()


@responses.activate
def test_cloud_list_discovery_vms(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/cloud/vms",
        json=["EXAMPLE"],
    )
    resp = pcce.cloud.list_discovery_vms()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "EXAMPLE"
