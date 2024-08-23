from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_audits_list_docker_access(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/access", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.audits.list_docker_access()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_docker_access(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/access/download", body=test_file.read())
    test_file.seek(0)
    resp = pcce.audits.download_docker_access()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_admission(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/admission", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.audits.list_admission()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_admission(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/admission/download", body=test_file.read())
    test_file.seek(0)
    resp = pcce.audits.download_admission()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_waas_agentless(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/firewall/app/agentless",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_waas_agentless()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_waas_agentless(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/agentless/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_waas_agentless()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_waas_agentless_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/agentless/timeslice")
    pcce.audits.get_waas_agentless_timeframe()


@responses.activate
def test_audits_list_waas_app_embedded(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/firewall/app/app-embedded",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_waas_app_embedded()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_waas_app_embedded(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/app-embedded/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_waas_app_embedded()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_waas_app_embedded_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/app-embedded/timeslice")
    pcce.audits.get_waas_app_embedded_timeframe()


@responses.activate
def test_audits_list_waas_container(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/firewall/app/container",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_waas_container()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_waas_container(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/container/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_waas_container()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_waas_container_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/container/timeslice")
    pcce.audits.get_waas_container_timeframe()


@responses.activate
def test_audits_list_waas_host(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/firewall/app/host",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_waas_host()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_waas_host(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/host/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_waas_host()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_waas_host_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/host/timeslice")
    pcce.audits.get_waas_host_timeframe()


@responses.activate
def test_audits_list_waas_serverless(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/firewall/app/serverless",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_waas_serverless()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_waas_serverless(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/serverless/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_waas_serverless()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_waas_serverless_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/firewall/app/serverless/timeslice")
    pcce.audits.get_waas_serverless_timeframe()


@responses.activate
def test_audits_list_cnns_container(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/firewall/network/container",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_cnns_container()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_cnns_container(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/firewall/network/container/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_cnns_container()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_cnns_host(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/firewall/network/host",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_cnns_host()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_cnns_host(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/firewall/network/host/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_cnns_host()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_incident(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/incidents", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.audits.list_incident()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_archive_incident(pcce):
    responses.add(responses.PATCH, "https://localhost:8083/api/v1/audits/incidents/acknowledge/1234")
    pcce.audits.archive_incident("1234")


@responses.activate
def test_audits_download_incident(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/incidents/download", body=test_file.read())
    test_file.seek(0)
    resp = pcce.audits.download_incident()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_kubernetes(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/kubernetes", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.audits.list_kubernetes()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_kubernetes(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/kubernetes/download", body=test_file.read())
    test_file.seek(0)
    resp = pcce.audits.download_kubernetes()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_management(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/mgmt", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.audits.list_management()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_management(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/mgmt/download", body=test_file.read())
    test_file.seek(0)
    resp = pcce.audits.download_management()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_management_filter(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/mgmt/filters")
    pcce.audits.get_management_filter()


@responses.activate
def test_audits_list_runtime_app_embeded(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/runtime/app-embedded",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_runtime_app_embeded()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_runtime_app_embeded(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/runtime/app-embedded/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_runtime_app_embeded()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_runtime_container(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/runtime/container",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_runtime_container()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_runtime_container(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/runtime/container/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_runtime_container()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_runtime_container_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/runtime/container/timeslice")
    pcce.audits.get_runtime_container_timeframe()


@responses.activate
def test_audits_list_runtime_file_integrity(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/runtime/file-integrity",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_runtime_file_integrity()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_runtime_file_integrity(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/runtime/file-integrity/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_runtime_file_integrity()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_runtime_host(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/runtime/host",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_runtime_host()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_runtime_host(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/runtime/host/download", body=test_file.read())
    test_file.seek(0)
    resp = pcce.audits.download_runtime_host()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_runtime_host_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/runtime/host/timeslice")
    pcce.audits.get_runtime_host_timeframe()


@responses.activate
def test_audits_list_runtime_log_inspection(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/runtime/log-inspection",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_runtime_log_inspection()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_runtime_log_inspection(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/runtime/log-inspection/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_runtime_log_inspection()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_list_runtime_serverless(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/audits/runtime/serverless",
        json=[{"string": "string"} for i in range(10)],
    )
    resp = pcce.audits.list_runtime_serverless()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_runtime_serverless(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/runtime/serverless/download", body=test_file.read()
    )
    test_file.seek(0)
    resp = pcce.audits.download_runtime_serverless()
    assert resp.read() == test_file.read()


@responses.activate
def test_audits_get_runtime_serverless_timeframe(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/runtime/serverless/timeslice")
    pcce.audits.get_runtime_serverless_timeframe()


@responses.activate
def test_audits_list_trust(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/audits/trust", json=[{"string": "string"} for i in range(10)]
    )
    resp = pcce.audits.list_trust()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"string": "string"}


@responses.activate
def test_audits_download_trust(pcce):
    test_file = BytesIO(b"this is a test")
    responses.add(responses.GET, "https://localhost:8083/api/v1/audits/trust/download", body=test_file.read())
    test_file.seek(0)
    resp = pcce.audits.download_trust()
    assert resp.read() == test_file.read()
