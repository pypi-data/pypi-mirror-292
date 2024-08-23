from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_hosts_list_scan_results(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/hosts", json=[{"string": "string"} for i in range(10)])
    resp = pcce.hosts.list_scan_results()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_hosts_download_scan_results(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/hosts/download",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.hosts.download_scan_results()
    assert test_file.read() == fobj.read()


@responses.activate
def test_hosts_resolve_host(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/hosts/evaluate")
    pcce.hosts.resolve_host()


@responses.activate
def test_hosts_get_host_info(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/hosts/info", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.hosts.get_host_info()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_hosts_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/hosts/scan")
    pcce.hosts.scan()
