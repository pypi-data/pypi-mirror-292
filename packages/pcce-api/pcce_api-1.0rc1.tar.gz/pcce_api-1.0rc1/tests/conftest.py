from __future__ import annotations

import pytest
import responses

from pcce import PCCE


@pytest.fixture
@responses.activate
def pcce():
    responses.add(
        responses.POST,
        "https://localhost:8083/api/v1/authenticate",
        json={"token": "string"},
    )
    return PCCE(url="https://localhost:8083", username="username", password="password")
