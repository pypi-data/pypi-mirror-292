from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_profiles_list_app_embedded(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/profiles/app-embedded",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.profiles.list_app_embedded()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_profiles_download_app_embedded(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/profiles/app-embedded/download",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.profiles.download_app_embedded()
    assert test_file.read() == fobj.read()


@responses.activate
def test_profiles_list_runtime_container(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/profiles/container",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.profiles.list_runtime_container()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_profiles_download_runtime_container(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/profiles/container/download",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.profiles.download_runtime_container()
    assert test_file.read() == fobj.read()


@responses.activate
def test_profiles_relearn_runtime_container(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/profiles/container/learn")
    pcce.profiles.relearn_runtime_container()


@responses.activate
def test_profiles_list_runtime_host(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/profiles/host",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.profiles.list_runtime_host()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_profiles_download_runtime_host(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/profiles/host/download",
        body=test_file.read(),
    )
    test_file.seek(0)
    fobj = pcce.profiles.download_runtime_host()
    assert test_file.read() == fobj.read()
