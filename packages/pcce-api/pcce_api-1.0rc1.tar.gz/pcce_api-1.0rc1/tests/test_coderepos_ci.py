from __future__ import annotations

import responses


@responses.activate
def test_coderepos_add(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/coderepos-ci")
    pcce.coderepos_ci.add(data={"_id": "string"})


@responses.activate
def test_coderepos_resolve(pcce):
    responses.add(responses.POST, "https://localhost:8083/api/v1/coderepos-ci/evaluate")
    pcce.coderepos_ci.resolve(data={"_id": "string"})
