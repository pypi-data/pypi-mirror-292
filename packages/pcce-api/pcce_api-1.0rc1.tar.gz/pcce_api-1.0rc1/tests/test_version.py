from __future__ import annotations

import responses


@responses.activate
def test_version_get(pcce):
    responses.add(responses.GET, "https://localhost:8083/api/v1/version")
    pcce.version.get()
