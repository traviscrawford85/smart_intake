"""
Minimal FastAPI backend for testing OAuth functionality
"""

import logging
import os
from contextlib import asynccontextmanager

import httpx

from clio_manage.routers.auth_routes import router as auth_router
from clio_manage.routers.triage_routes import router as triage_router

try:
    from api.analytics_router import router as analytics_router
except ImportError:
    analytics_router = None
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan events"""
    logger.info("🚀 Starting Clio KPI Dashboard Backend (OAuth Test Mode)")

    # Initialize database
    try:
        from db import Base, token_engine

        logger.info("📦 Creating token database tables...")
        Base.metadata.create_all(bind=token_engine)
        logger.info("✅ Token database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        # Log more details for debugging
        import traceback

        logger.error(f"Database error details: {traceback.format_exc()}")

    yield
    logger.info("⏹️ Shutting down backend")


# Initialize FastAPI app
app = FastAPI(
    title="Clio KPI Dashboard Backend",
    description="Backend API for the Clio Legal KPI Dashboard",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from clio_manage.routers.analytics_router import router as analytics_router

# Register authentication routes
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])

# Register triage workflow routes
app.include_router(triage_router, prefix="/api/triage", tags=["Triage"])

# Register analytics/dashboard routes if available
if analytics_router:
    app.include_router(analytics_router, prefix="/api/analytics", tags=["Analytics"])


# Simple health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "clio-kpi-backend", "mode": "oauth-test"}


# Dashboard redirect endpoint for Clio custom actions
from typing import Optional


@app.get("/dashboard")
async def dashboard_redirect(
    clio_action: Optional[str] = None,
    ui_ref: Optional[str] = None,
    context_id: Optional[str] = None,
    matter_id: Optional[str] = None,
):
    """
    Redirect dashboard requests to Streamlit frontend on company domain
    This endpoint handles requests from Clio custom actions and forwards them to the Streamlit dashboard
    """
    # Use company domain for Streamlit frontend
    streamlit_url = os.getenv("STREAMLIT_URL", "https://dashboard.dev.cfelab.com")

    # Preserve all query parameters for the Streamlit frontend
    params = []
    if clio_action:
        params.append(f"clio_action={clio_action}")
    if ui_ref:
        params.append(f"ui_ref={ui_ref}")
    if context_id:
        params.append(f"context_id={context_id}")
    if matter_id:
        params.append(f"matter_id={matter_id}")

    # Construct the full Streamlit URL
    if params:
        dashboard_url = f"{streamlit_url}?{'&'.join(params)}"
    else:
        dashboard_url = streamlit_url

    logger.info(f"🔄 Redirecting to Streamlit dashboard: {dashboard_url}")

    # Redirect to Streamlit on company domain
    return RedirectResponse(url=dashboard_url, status_code=302)


# Proxy endpoint to serve Streamlit through the same domain
@app.get("/app/{path:path}")
async def proxy_to_streamlit(path: str, request: Request):
    """
    Proxy requests to Streamlit frontend
    This allows serving the Streamlit app through the same ngrok domain
    """
    streamlit_base = "http://localhost:8501"

    # Construct the target URL
    target_url = f"{streamlit_base}/{path}"
    if request.url.query:
        target_url += f"?{request.url.query}"

    logger.info(f"🔄 Proxying to Streamlit: {target_url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url, timeout=30)
            return response.content
    except Exception as e:
        logger.error(f"❌ Proxy error: {e}")
        return {"error": "Failed to proxy to Streamlit"}


# Root app proxy - serve Streamlit at the root when accessed with clio parameters
@app.get("/app")
async def proxy_root_to_streamlit(request: Request):
    """
    Proxy root app requests to Streamlit frontend
    """
    streamlit_base = "http://localhost:8501"

    # Construct the target URL with query parameters
    target_url = streamlit_base
    if request.url.query:
        target_url += f"?{request.url.query}"

    logger.info(f"🔄 Proxying root to Streamlit: {target_url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(target_url, timeout=30)
            return response.content
    except Exception as e:
        logger.error(f"❌ Proxy error: {e}")
        return {"error": "Failed to proxy to Streamlit"}


# Simple root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Clio KPI Dashboard Backend",
        "status": "running",
        "mode": "oauth-test",
        "endpoints": {
            "auth": "/auth",
            "health": "/health",
            "analytics": "/api/analytics",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
