import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.chat_routes import router as chat_router
from app.config.settings import settings

# Configure high-density system logging stream configurations
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexusmind")

# 🎯 Centralized initialization pulling dynamic config and pyproject.toml version info
app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description=settings.app.description,
    docs_url="/docs",
)

# Mount Cross-Origin Resource Sharing rules to connect safely with Streamlit on port 8501
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount your clean endpoint routes (Naked mount since chat_routes.py handles its own /api prefix)
app.include_router(chat_router)


@app.get("/health", tags=["system"])
async def health_check():
    """System heartbeat connectivity endpoint routing monitor."""
    return {
        "status": "healthy",
        "service": f"{settings.app.name} Backend Engine Gateway Instance",
        "version": settings.app.version,
        "environment_online": True,
    }
