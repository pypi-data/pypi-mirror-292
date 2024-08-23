from __future__ import annotations

from datetime import datetime

import pytest

from pcce.schema.agentless import AgentlessSchema
from pcce.schema.utils import PCCEDateTime, get_schema_info


@pytest.fixture
def pccedatetime():
    return PCCEDateTime()


def test_serialize_valid_datetime(pccedatetime):
    dt = datetime(2024, 8, 5, 15, 30, 45, 123456)
    serialized = pccedatetime._serialize(dt, None, None)
    assert serialized == "2024-08-05T15:30:45.123"


def test_serialize_none(pccedatetime):
    assert pccedatetime._serialize(None, None, None) is None


def test_deserialize_valid_datetime_string(pccedatetime):
    dt_string = "2024-08-05T15:30:45.123456+0000"
    dt = pccedatetime._deserialize(dt_string, None, None)
    assert dt == datetime.strptime(dt_string, "%Y-%m-%dT%H:%M:%S.%f%z")


def test_get_schema_info():
    get_schema_info(AgentlessSchema())
