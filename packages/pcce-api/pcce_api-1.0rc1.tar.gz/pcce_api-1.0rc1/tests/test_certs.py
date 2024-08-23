from __future__ import annotations

import responses


@responses.activate
def test_certs_get_ca_pem(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/certs/ca.pem",
        json="EXAMPLE",
    )
    resp = pcce.certs.get_ca_pem()
    assert resp == "EXAMPLE"


@responses.activate
def test_certs_get_server_cert(pcce):
    responses.add(
        responses.GET,
        "https://localhost:8083/api/v1/certs/server-cert.sh",
        json="EXAMPLE",
    )
    resp = pcce.certs.get_server_cert()
    assert resp == "EXAMPLE"
