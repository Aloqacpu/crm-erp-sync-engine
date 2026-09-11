import httpx
import pytest

from app.services.erp_client import ErpClient, ErpClientError


@pytest.mark.asyncio
async def test_erp_client_retries_transient_failure():
    calls = 0

    async def handler(request: httpx.Request) -> httpx.Response:
        nonlocal calls
        calls += 1
        return httpx.Response(500 if calls < 3 else 201, json={"erp_id": "42"}, request=request)

    client = ErpClient("http://erp", "", 2, 3, 0, httpx.MockTransport(handler))
    assert await client.create_order({"id": "crm-1"}) == {"erp_id": "42"}
    assert calls == 3


@pytest.mark.asyncio
async def test_erp_client_raises_after_exhausting_retries():
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, request=request)

    client = ErpClient("http://erp", "", 2, 1, 0, httpx.MockTransport(handler))
    with pytest.raises(ErpClientError):
        await client.create_order({"id": "crm-1"})
