from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_stats_get_app_firewall(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/app-firewall/count", json=12)
    resp = pcce.stats.get_app_firewall()
    assert resp == 12


@responses.activate
def test_stats_get_compliance(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/compliance", json={"key": "value"})
    resp = pcce.stats.get_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_stats_download_compliance(pcce):
    fobj = BytesIO(b"test content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/compliance/download", body=fobj.read())
    fobj.seek(0)
    resp = pcce.stats.download_compliance()
    assert resp.read() == fobj.read()


@responses.activate
def test_stats_fresh_compliance(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/stats/compliance/refresh", json={"key": "value"})
    resp = pcce.stats.fresh_compliance()
    assert resp == {"key": "value"}


@responses.activate
def test_stats_get_daily(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/stats/daily", json=[{"key": "value"} for i in range(10)]
    )
    resp = pcce.stats.get_daily()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_stats_get_dashboard(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/dashboard", json={"key": "value"})
    resp = pcce.stats.get_dashboard()
    assert resp == {"key": "value"}


@responses.activate
def test_stats_get_event(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/events", json={"key": "value"})
    resp = pcce.stats.get_event()
    assert resp == {"key": "value"}


@responses.activate
def test_stats_get_license(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/license", json={"key": "value"})
    resp = pcce.stats.get_license()
    assert resp == {"key": "value"}


@responses.activate
def test_stats_get_vulnerability(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/vulnerabilities", json={"key": "value"})
    resp = pcce.stats.get_vulnerability()
    assert resp == {"key": "value"}


@responses.activate
def test_stats_download_vulnerability(pcce):
    fobj = BytesIO(b"test content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/stats/vulnerabilities/download", body=fobj.read())
    fobj.seek(0)
    resp = pcce.stats.download_vulnerability()
    assert resp.read() == fobj.read()


@responses.activate
def test_stats_get_impacted_resource_vulnerability(pcce):
    responses.add(
        responses.GET, "https://localhost:8083/api/v1/stats/vulnerabilities/impacted-resources", json={"key": "value"}
    )
    resp = pcce.stats.get_impacted_resource_vulnerability()
    assert resp == {"key": "value"}


@responses.activate
def test_stats_download_impacted_resource_vulnerability(pcce):
    fobj = BytesIO(b"test content")
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/stats/vulnerabilities/impacted-resources/download",
        body=fobj.read(),
    )
    fobj.seek(0)
    resp = pcce.stats.download_impacted_resource_vulnerability()
    assert resp.read() == fobj.read()


@responses.activate
def test_stats_fresh_vulnerability(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/stats/vulnerabilities/refresh", json={"key": "value"})
    resp = pcce.stats.fresh_vulnerability()
    assert resp == {"key": "value"}
