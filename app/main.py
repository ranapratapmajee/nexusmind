# path: app/main.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as chat_router
from app.settings import settings

logging.basicConfig(
    level=settings.LOG_LEVEL, 
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("nexusmind.main")

app = FastAPI(
    title=f"{settings.bot_name} Core Engine Platform",
    version="2.0.0",
    description="High-density dynamic agent graph backend platform for NexusMind.",
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.get("/health", tags=["system"])
async def health_check():
    return {
        "status": "healthy",
        "service": f"{settings.bot_name} Backend Engine Instance",
        "environment_online": True,
    }