import asyncio
from typing import Any

import httpx


class ErpClientError(RuntimeError):
    pass


class ErpClient:
    def __init__(self, base_url: str, token: str, timeout: float, max_retries: int, base_delay: float, transport: httpx.AsyncBaseTransport | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.transport = transport

    async def create_order(self, payload: dict[str, Any]) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout, transport=self.transport) as client:
            last_error: Exception | None = None
            for attempt in range(self.max_retries + 1):
                try:
                    response = await client.post("/api/v1/erp/orders", json=payload, headers=headers)
                    if response.status_code >= 500:
                        raise httpx.HTTPStatusError("ERP server error", request=response.request, response=response)
                    response.raise_for_status()
                    return response.json()
                except (httpx.HTTPError, ValueError) as exc:
                    last_error = exc
                    if attempt >= self.max_retries:
                        break
                    await asyncio.sleep(self.base_delay * (2**attempt))
            raise ErpClientError(f"ERP order request failed after {self.max_retries + 1} attempts: {last_error}") from last_error
