from sqlalchemy.ext.asyncio import AsyncSession

from app.models import SyncLog, SyncStatus
from app.schemas.crm import CrmOrderCreated
from app.schemas.erp import ErpOrder
from app.services.erp_client import ErpClient, ErpClientError


class SyncService:
    def __init__(self, client: ErpClient):
        self.client = client

    async def sync_order(self, order: CrmOrderCreated, session: AsyncSession) -> SyncLog:
        erp_order = ErpOrder.from_crm(order)
        log = SyncLog(crm_order_id=order.order_id, crm_payload=order.model_dump(mode="json"), status=SyncStatus.PENDING)
        session.add(log)
        await session.flush()
        try:
            response = await self.client.create_order(erp_order.model_dump(mode="json"))
            log.status = SyncStatus.SUCCESS
            log.erp_payload = response
        except ErpClientError as exc:
            log.status = SyncStatus.FAILED
            log.error_message = str(exc)
            raise
        finally:
            log.attempts += 1
            await session.commit()
        return log
