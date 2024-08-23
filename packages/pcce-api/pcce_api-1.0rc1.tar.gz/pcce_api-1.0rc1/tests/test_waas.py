from __future__ import annotations

from io import BytesIO

import responses


@responses.activate
def test_waas_scan(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/waas/openapi-scans", json={"key": "value"})
    fobj = BytesIO(b"Test file content")
    resp = pcce.waas.scan(fobj=fobj)
    assert resp == {"key": "value"}
