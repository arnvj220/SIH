from fastapi import FastAPI

from .api.router import router as api_router

app = FastAPI(
    title="QDS API",
    version="1.0.0",
)

app.include_router(api_router)


@app.get("/health")
def health() -> dict[str, str]:
    """Basic service health check."""
    return {"status": "ok"}