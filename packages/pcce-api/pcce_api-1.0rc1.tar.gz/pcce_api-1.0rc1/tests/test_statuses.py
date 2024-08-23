from __future__ import annotations

import responses


@responses.activate
def test_statuses_get_registry_scan(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/statuses/registry", json={"key": "value"})
    resp = pcce.statuses.get_registry_scan()
    assert resp == {"key": "value"}
