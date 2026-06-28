# path: app/main.py

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api_routes import router as chat_router
from app.settings import settings

# 1. Setup Robust System-Wide Logging Topology
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=log_level, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexusmind.main")

# 2. Lifecycle Context: Handles startup validation logic smoothly
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"🚀 Initializing {settings.APP_NAME} Graph Engine Application...")
    logger.info(f"🤖 Target Local Hardware Model Node: [{settings.OLLAMA_MODEL}]")
    yield
    logger.info(f"🛑 Shutting down {settings.APP_NAME} Graph Engine Application...")

# 3. Initialize Core FastAPI Application Core Instance
app = FastAPI(
    title=f"{settings.bot_name} Core Engine Platform",
    version="2.0.0",
    description="High-density dynamic agent graph backend platform for NexusMind.",
    docs_url="/docs",
    lifespan=lifespan
)

# 4. Configure Cross-Origin Resource Sharing (CORS) Bounds
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 5. Register Orchestration Endpoints
app.include_router(chat_router)

# =========================================================================
# ⚙️ SYSTEM LIFECYCLE MANAGEMENT ENDPOINTS
# =========================================================================

@app.get("/health", tags=["system"])
async def health_check():
    """Returns baseline system operational structural availability metrics."""
    return {
        "status": "healthy",
        "service": f"{settings.bot_name} Backend Engine Instance",
        "environment": settings.APP_ENV,
    }
