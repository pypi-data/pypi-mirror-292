from __future__ import annotations

from io import BytesIO

import responses

DEFENDER = {"category": "container", "usingOldCA": True, "version": "string", "vpcObserver": True}


@responses.activate
def test_defenders_list_deployed(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/defenders", json=[DEFENDER for i in range(10)])
    resp = pcce.defenders.list_deployed()
    assert isinstance(resp, list)
    for item in resp:
        assert item == DEFENDER


@responses.activate
def test_defenders_generate_dockerfile_for_app_embedded(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/app-embedded", body=test_file.read())
    test_file.seek(0)
    fobj = pcce.defenders.generate_dockerfile_for_app_embedded(
        data={
            "appID": "my-app",
            "consoleAddr": "https://localhost:8083",
            "dataFolder": "/var/lib/docker/containers/twistlock/tmp",
            "dockerfile": "/var/lib/docker/overlay2/183e9e3ec933ba2363bcf6066b7605d99bfcf4dce84f72eeeba0f616c679cf48",
        }
    )
    assert test_file.read() == fobj.read()


@responses.activate
def test_defenders_generate_daemon_set(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/daemonset.yaml", body=test_file.read())
    test_file.seek(0)
    fobj = pcce.defenders.generate_daemon_set(
        data={"orchestration": "container", "consoleAddr": "servo-vmware71", "namespace": "twistlock"}
    )
    assert test_file.read() == fobj.read()


@responses.activate
def test_defenders_download_deployed(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/defenders/download", body=test_file.read())
    test_file.seek(0)
    fobj = pcce.defenders.download_deployed()
    assert test_file.read() == fobj.read()


@responses.activate
def test_defenders_generate_protected_json_fargate(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/fargate.json", body=test_file.read())
    test_file.seek(0)
    fobj = pcce.defenders.generate_protected_json_fargate()
    assert test_file.read() == fobj.read()


@responses.activate
def test_defenders_generate_protected_yaml_fargate(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/fargate.yaml", body=test_file.read())
    test_file.seek(0)
    fobj = pcce.defenders.generate_protected_yaml_fargate()
    assert test_file.read() == fobj.read()


@responses.activate
def test_defenders_generate_helm_deployment(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.POST, "https://localhost:8083/api/v1/defenders/twistlock-defender-helm.tar.gz", body=test_file.read()
    )
    test_file.seek(0)
    fobj = pcce.defenders.generate_helm_deployment(
        data={"orchestration": "container", "consoleAddr": "servo-vmware71", "namespace": "twistlock"}
    )
    assert test_file.read() == fobj.read()


@responses.activate
def test_defenders_get_image_name(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/defenders/image-name", json="TEST")
    resp = pcce.defenders.get_image_name()
    assert resp == "TEST"


@responses.activate
def test_defenders_get_cert_bundle(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/defenders/install-bundle", json={"key": "value"})
    resp = pcce.defenders.get_cert_bundle()
    assert resp == {"key": "value"}


@responses.activate
def test_defenders_get_defender_name(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/defenders/names", json=["names" for i in range(10)])
    resp = pcce.defenders.get_defender_name()
    assert isinstance(resp, list)
    for item in resp:
        assert item == "names"


@responses.activate
def test_defenders_generate_serverless(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/serverless/bundle", body=test_file.read())
    test_file.seek(0)
    fobj = pcce.defenders.generate_serverless(data={"provider": ["aws"], "runtime": ["nodejs14.x"]})
    assert test_file.read() == fobj.read()


@responses.activate
def test_defenders_list_summary(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/defenders/summary", json=[DEFENDER for i in range(10)])
    resp = pcce.defenders.list_summary()
    assert isinstance(resp, list)
    for item in resp:
        assert item == DEFENDER


@responses.activate
def test_defenders_upgrade_connected_linux(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/upgrade")
    pcce.defenders.upgrade_connected_linux()


@responses.activate
def test_defenders_delete(pcce):
    responses.add(responses.DELETE, "https://localhost:8083/api/v1/defenders/1234")
    pcce.defenders.delete("1234")


@responses.activate
def test_defenders_update_configuration(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/1234/features")
    pcce.defenders.update_configuration("1234")


@responses.activate
def test_defenders_restart(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/1234/restart")
    pcce.defenders.restart("1234")


@responses.activate
def test_defenders_upgrade(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/defenders/1234/upgrade")
    pcce.defenders.upgrade("1234")
