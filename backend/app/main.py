from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.router import router as api_router
from .core.config import settings
from .db.database import create_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        create_tables()
    except Exception as exc:
        print(f"[startup] create_tables failed (DB down?): {exc}")
    yield


app = FastAPI(
    title="QDS API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}