from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import init_database
from app.routes.sync import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_database()
    yield


app = FastAPI(title="CRM ERP Sync Engine", version="1.0.0", lifespan=lifespan)
app.include_router(router, prefix="/api/v1")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
