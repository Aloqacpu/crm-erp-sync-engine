import httpx
import pytest

from app.routes.sync import service
from app.services.erp_client import ErpClient


def payload() -> dict:
    return {
        "order_id": "crm-100",
        "lead": {"name": "Ada Lovelace", "email": "ada@example.com", "phone": "0044 (20) 1234-5678"},
        "items": [{"sku": "CPU-1", "name": "Processor", "quantity": 2, "unit_price": "50.00"}],
        "status": "confirmed", "total_price": "100.00", "currency": "usd",
    }


@pytest.mark.asyncio
async def test_order_flow_transforms_and_logs_success(client, monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/api/v1/erp/orders"
        body = request.read()
        assert b"+44" in body
        return httpx.Response(201, json={"erp_id": "erp-100"}, request=request)

    monkeypatch.setattr("app.routes.sync.service", lambda: __import__("app.services.sync_service", fromlist=["SyncService"]).SyncService(ErpClient("http://erp", "", 2, 0, 0, httpx.MockTransport(handler))))
    response = await client.post("/api/v1/crm/order-created", json=payload())
    assert response.status_code == 201
    assert response.json()["status"] == "SUCCESS"


@pytest.mark.asyncio
async def test_order_flow_returns_bad_gateway_on_erp_failure(client, monkeypatch):
    async def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503, request=request)

    monkeypatch.setattr("app.routes.sync.service", lambda: __import__("app.services.sync_service", fromlist=["SyncService"]).SyncService(ErpClient("http://erp", "", 2, 0, 0, httpx.MockTransport(handler))))
    response = await client.post("/api/v1/crm/order-created", json=payload())
    assert response.status_code == 502
