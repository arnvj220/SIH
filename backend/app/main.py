from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pymongo.errors import PyMongoError

from .api.router import router as api_router
from .core.config import settings
from .db.database import client, initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        initialize_database()
    except PyMongoError as exc:
        print(
            "[startup] MongoDB unavailable "
            f"({type(exc).__name__}); database-backed endpoints may fail"
        )
    print("[startup] Qureka API starting")
    yield
    client.close()
    print("[shutdown] Qureka API stopping")


app = FastAPI(
    title="Qureka API",
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