from __future__ import annotations

import pytest
import responses

from pcce import PCCE


def test_invalid_url():
    with pytest.raises(TypeError):
        PCCE(url="://localhost:8834", username="username", password="password")


@responses.activate
def test_pcce_basic_auth():
    """
    Test basic authenticate
    """
    responses.add(
        responses.POST,
        "https://localhost:8083/api/v1/authenticate",
        json={"token": "string"},
    )
    PCCE(url="https://localhost:8083", username="username", password="password")


@responses.activate
def test_pcce_token_auth():
    """
    Test session authenticate
    """
    responses.add(
        responses.POST,
        "https://localhost:8083/api/v1/authenticate",
        json={"token": "string"},
    )
    PCCE(url="https://localhost:8083", username="username", password="password")


@responses.activate
def test_pcce_client_cert_auth():
    """
    Test client cert
    """
    responses.add(
        responses.POST,
        "https://localhost:8083/api/v1/authenticate-client",
        json={"token": "string"},
    )
    PCCE(url="https://localhost:8083", cert_path="/path/client.cert")
