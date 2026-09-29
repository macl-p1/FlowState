"""OrchestrAI Backend — FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from fastapi import APIRouter

from app.config import settings
from app.database import engine, Base
from app.api import workflows, runs, approvals, tools, custom_tools


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
    yield
    # Cleanup if needed


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

# Routers — health first, then feature routers
app.include_router(health_router, prefix="/api", tags=["health"])
app.include_router(workflows.router, prefix="/api", tags=["workflows"])
app.include_router(runs.router, prefix="/api", tags=["runs"])
app.include_router(approvals.router, prefix="/api", tags=["approvals"])
app.include_router(custom_tools.router, prefix="/api", tags=["custom-tools"])
app.include_router(tools.router, prefix="/api", tags=["tools"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
