from __future__ import annotations

import responses


@responses.activate
def test_ping(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/_ping")
    pcce.ping._ping()
