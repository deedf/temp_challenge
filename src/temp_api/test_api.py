"""Unittests for temperature API"""

from unittest import mock
from fastapi import HTTPException

import pytest

import temp_api.api

temp_api.api.requests_client = mock.AsyncMock()
temp_api.api.app = mock.MagicMock()
temp_api.api.registry = mock.MagicMock()
temp_api.api.g = mock.MagicMock()
temp_api.api.push_to_gateway = mock.MagicMock()


@pytest.mark.asyncio
async def test_read_temperature():
    """Test read_temperature"""
    json = mock.MagicMock()
    json.return_value = {"data": {"result": [{"value": [1, 42]}]}}
    temp_api.api.requests_client.get.return_value.json = json
    temp = await temp_api.api.read_temperature("a", "b")
    temp_api.api.requests_client.get.assert_awaited()
    assert temp == 42


@pytest.mark.asyncio
async def test_read_temperature_no_data():
    """Test read_temperature with no data"""
    json = mock.MagicMock()
    json.return_value = {"data": {"result": []}}
    temp_api.api.requests_client.get.return_value.json = json
    with pytest.raises(HTTPException):
        await temp_api.api.read_temperature("a", "b")
    temp_api.api.requests_client.get.assert_awaited()


@pytest.mark.asyncio
async def test_write_temperature():
    """Test write_temperature"""
    await temp_api.api.write_temperature("a", "b", 42)
    temp_api.api.g.assert_has_calls(
        [mock.call.labels(building="a", room="b"), mock.call.labels().set(42)]
    )
    temp_api.api.push_to_gateway.assert_has_calls(
        [mock.call("http://localhost:9091/", job="api", registry=temp_api.api.registry)]
    )
