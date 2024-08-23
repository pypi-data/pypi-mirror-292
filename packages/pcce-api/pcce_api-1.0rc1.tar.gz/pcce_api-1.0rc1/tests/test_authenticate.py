from __future__ import annotations

import responses


@responses.activate
def test_authenticate_get(pcce):
    responses.add(
        responses.POST,
        "https://localhost:8083/api/v1/authenticate",
        json={"token": "ACCESS_TOKEN"},
    )
    resp = pcce.authenticate.get(username="username", password="password")
    assert resp == "ACCESS_TOKEN"
