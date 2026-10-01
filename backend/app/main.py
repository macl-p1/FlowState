"""OrchestrAI Backend — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import APIRouter

from app.config import settings
from app.database import engine, Base
from app.api import workflows, runs, approvals, tools, custom_tools, integrations
from app.api.auth import get_api_key
from app.api import genealogy
from app.api import suggestions, analytics, quality, triggers
from app.engine.jobs import get_worker, recover_interrupted
from app.utils.graph import normalize_stored_graphs
from fastapi import Depends


# Health endpoint (must be defined before inclusion)
health_router = APIRouter()

@health_router.get("/health")
async def health():
    return {"status": "healthy", "service": "orchestr-ai", "version": "0.1.0"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    normalize_stored_graphs(engine)  # one-time fix for workflows saved in canvas shape (idempotent)
    worker = get_worker(engine)
    if settings.worker_enabled:
        recover_interrupted(engine)  # runs a crash left mid-flight -> failed (replayable)
        worker.kick()  # fires schedule triggers and starts queued runs
    yield
    await worker.stop()


app = FastAPI(
    title="OrchestrAI API",
    description="Universal Workflow Agent Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — health is public, all others require API key
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(workflows.router, prefix="/api", tags=["workflows"], dependencies=[Depends(get_api_key)])
app.include_router(runs.router, prefix="/api", tags=["runs"], dependencies=[Depends(get_api_key)])
app.include_router(approvals.router, prefix="/api", tags=["approvals"], dependencies=[Depends(get_api_key)])
app.include_router(custom_tools.router, prefix="/api", tags=["custom-tools"], dependencies=[Depends(get_api_key)])
app.include_router(integrations.router, prefix="/api", tags=["integrations"], dependencies=[Depends(get_api_key)])
app.include_router(tools.router, prefix="/api", tags=["tools"], dependencies=[Depends(get_api_key)])
app.include_router(genealogy.router, prefix="/api", tags=["genealogy"], dependencies=[Depends(get_api_key)])
app.include_router(suggestions.router, prefix="/api", tags=["suggestions"], dependencies=[Depends(get_api_key)])
app.include_router(analytics.router, prefix="/api", tags=["analytics"], dependencies=[Depends(get_api_key)])
app.include_router(triggers.router, prefix="/api", tags=["triggers"], dependencies=[Depends(get_api_key)])
app.include_router(triggers.hooks_router, prefix="/api", tags=["webhooks"])  # token-in-URL auth, no API key
app.include_router(quality.router, prefix="/api", tags=["quality"], dependencies=[Depends(get_api_key)])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
