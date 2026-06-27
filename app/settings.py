# path: app/settings.py

import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

# 🎯 Establish Project Root
PROJECT_ROOT = Path(__file__).resolve().parent.parent

class AppMetaWrapper:
    """Mock metadata wrapper to fulfill frontend settings.app namespace properties cleanly."""
    def __init__(self, name: str, version: str):
        self.name = name
        self.version = version

class NexusSettings(BaseSettings):
    """Unified application configurations parsed directly from the environment."""
    
    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Core Variables
    APP_ENV: str = "development"
    LOG_LEVEL: str = "INFO"
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001
    
    FRONTEND_HOST: str = "0.0.0.0"
    FRONTEND_PORT: int = 8501
    
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION: str = "knowledgebase"
    
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 3000
    
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"
    
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    
    OFFLINE_PDF_DIR: str = "./data"

    # Shared properties for quick backward compatibility
    @property
    def bot_name(self) -> str:
        return "Nexa"

    @property
    def top_k(self) -> int:
        return 6

    # 🟢 Bridge property to maps settings.app.name / settings.app.version seamlessly to the UI
    @property
    def app(self) -> AppMetaWrapper:
        return AppMetaWrapper(name="NexusMind", version="2.0.0")

# Singleton Instance
settings = NexusSettings()