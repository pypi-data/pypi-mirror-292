from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_images_list_scan_results(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/images", json=[{"string": "string"} for i in range(10)])
    resp = pcce.images.list_scan_results()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_images_download_scan_results(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/images/download",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.images.download_scan_results()
    assert test_file.read() == fobj.read()


@responses.activate
def test_images_resolve_host(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/images/evaluate")
    pcce.images.resolve(images={})


@responses.activate
def test_images_list_names(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/images/names", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.images.list_names()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_images_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/images/scan")
    pcce.images.scan()


@responses.activate
def test_images_download_app_embeded(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/images/twistlock_defender_app_embedded.tar.gz",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.images.download_app_embeded()
    assert test_file.read() == fobj.read()


@responses.activate
def test_images_download_serverless(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.POST,
        "https://localhost:8083/api/v1/images/twistlock_defender_layer.zip",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.images.download_serverless()
    assert test_file.read() == fobj.read()
