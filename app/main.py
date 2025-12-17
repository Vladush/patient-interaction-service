from contextlib import asynccontextmanager
from datetime import datetime, timezone

import asyncio
from fastapi import FastAPI, Depends, Request, Response
from sqlmodel import Session, text

from app.api.v1.api import api_router
from app.core.database import get_session, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield



API_DESCRIPTION = "Patient Documentation System API. System-strict, Audit-ready, RESTful."

tags_metadata = [
    {"name": "patients", "description": "Patient demographics."},
    {"name": "interactions", "description": "Clinical documentation."},
    {"name": "configuration", "description": "Reference data management."},
]

# Add the global dependency so Swagger UI shows the input field for every endpoint
app = FastAPI(
    title="HealthTech Patient Documentation System",
    description=API_DESCRIPTION,
    version="0.1.0",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)


@app.middleware("http")
async def chaos_middleware(request: Request, call_next):
    """
    Fault Tolerance testing.
    Header 'X-Simulation-Mode': 'error' | 'latency'
    """
    simulation_mode = request.headers.get("X-Simulation-Mode")
    
    if simulation_mode == "error":
        # Simulate catastrophic failure
        return Response(
            content=f"Simulated Failure Triggered via X-Simulation-Mode: {simulation_mode}",
            status_code=503,
        )
        
    if simulation_mode == "latency":
        # Simulate network lag
        await asyncio.sleep(2.0)
        
    response = await call_next(request)
    return response


app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check(detail: bool = False, session: Session = Depends(get_session)):
    """Health check endpoint."""
    if not detail:
        return {"status": "ok"}
        
    health_status = {
        "status": "ok",
        "version": app.version,
        "database": "unknown",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        session.exec(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        health_status["status"] = "degraded"
        health_status["database"] = "disconnected"
        health_status["error"] = str(e)
        
    return health_status
