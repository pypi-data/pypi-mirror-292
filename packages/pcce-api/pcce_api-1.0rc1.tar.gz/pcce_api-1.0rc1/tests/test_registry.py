from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_registry_list(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/registry", json=["address" for i in range(10)])
    resp = pcce.registry.list()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "address"


@responses.activate
def test_registry_download(pcce):
    fobj = BytesIO(b"test content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/registry/download", body=fobj.read())
    fobj.seek(0)
    resp = pcce.registry.download()
    assert resp.read() == fobj.read()


@responses.activate
def test_registry_list_name(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/registry/names", json=["string" for i in range(10)])
    resp = pcce.registry.list_name()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "string"


@responses.activate
def test_registry_add_registry(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/registry/webhook/webhook")
    pcce.registry.add_webhook(
        data={"action": "string", "artifactory": {}, "domain": "string", "event_type": "string", "type": "string"}
    )


@responses.activate
def test_registry_remove_webhook(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/registry/webhook/webhook")
    pcce.registry.remove_webhook()


@responses.activate
def test_registry_progress(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/registry/progress", json=["string" for i in range(10)])
    resp = pcce.registry.progress()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "string"


@responses.activate
def test_registry_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/registry/scan")
    pcce.registry.scan(data={"tag": {"registry": "REGISTRY", "repo": "REPO", "tag": "TAG", "digest": "DIGEST"}})


@responses.activate
def test_registry_scan_registries(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/registry/scan/select")
    pcce.registry.scan_registries(
        data={"tag": {"registry": "REGISTRY", "repo": "REPO", "tag": "TAG", "digest": "DIGEST"}}
    )


@responses.activate
def test_registry_stop(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/registry/stop")
    pcce.registry.stop()
