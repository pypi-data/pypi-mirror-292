from __future__ import annotations

import responses


@responses.activate
def test_authenticate_client_get(pcce):
    responses.add(
        responses.POST,
        "https://localhost:8083/api/v1/authenticate-client",
        json={"role": "admin", "token": "ACCESS_TOKEN"},
    )
    resp = pcce.authenticate_client.get("path_cert")
    assert resp == "ACCESS_TOKEN"
