from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_session
from app.schemas.crm import CrmOrderCreated
from app.services.erp_client import ErpClient, ErpClientError
from app.services.sync_service import SyncService

router = APIRouter()


def service() -> SyncService:
    config = get_settings()
    return SyncService(ErpClient(config.erp_base_url, config.erp_api_token, config.erp_timeout_seconds, config.erp_max_retries, config.retry_base_delay))


@router.post("/crm/order-created", status_code=status.HTTP_201_CREATED)
async def order_created(order: CrmOrderCreated, db: AsyncSession = Depends(get_session)):
    try:
        log = await service().sync_order(order, db)
    except ErpClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return {"sync_id": log.id, "status": log.status.value, "erp_payload": log.erp_payload}
