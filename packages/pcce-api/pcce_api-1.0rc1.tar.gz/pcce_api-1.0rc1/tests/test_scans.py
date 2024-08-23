from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_scans_list_ci_image_result(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/scans", json=[{"key": "value"} for i in range(10)])
    resp = pcce.scans.list_ci_image_result()
    assert isinstance(resp, list)
    for item in resp:
        assert item == {"key": "value"}


@responses.activate
def test_scans_get_ci_image_result(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/scans/scan1")
    pcce.scans.get_ci_image_result(_id="scan1")


@responses.activate
def test_scans_add_cli_result(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/scans")
    pcce.scans.add_cli_result(
        data={
            "_id": "string",
            "build": "string",
            "complianceFailureSummary": "string",
            "entityInfo": {
                "Secrets": ["string"],
                "_id": "string",
                "agentless": True,
            },
            "jobName": "string",
            "pass": True,
            "time": "2024-08-02T20:22:08.684Z",
            "version": "string",
            "vulnFailureSummary": "string",
        }
    )


@responses.activate
def test_scans_download_ci_image_result(pcce):
    fobj = BytesIO(b"test content")
    responses.add(responses.GET, "https://localhost:8083/api/v1/scans/download", body=fobj.read())
    fobj.seek(0)
    resp = pcce.scans.download_ci_image_result()
    assert resp.read() == fobj.read()
