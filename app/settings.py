# path: app/settings.py

from typing import Optional, Any
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

class AppSettings(BaseSettings):
    """🧠 NexusMind Central Configuration Management Core Layer.
    Automatically parses environment configurations using type-safe declarations.
    """
    # ====== Environment ======
    APP_NAME: str = "NexusMind"
    APP_ENV: str = "development"
    bot_name: str = "Nexa"

    # ====== API (FastAPI) ======
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8001

    # ====== Frontend (Streamlit) ======
    FRONTEND_HOST: str = "0.0.0.0"
    FRONTEND_PORT: int = 8501
    BACKEND_API_URL: str = "http://localhost:8001"

    # ====== ChromaDB Vector Store ======
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8000
    CHROMA_COLLECTION: str = "document_chunks"

    # ====== Neo4j Graph Database ======
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "rana1234"
    NEO4J_DATABASE: str = "neo4j"

    # ====== MCP Server ======
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 3000
    MCP_TRANSPORT: str = "http"

    # ====== Ollama (Local LLM) ======
    OLLAMA_MODEL: str = "qwen2.5-coder:7b"
    OLLAMA_EMBED_MODEL: str = "nomic-embed-text"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # ====== Cloud LLM Secrets ======
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None

    # ====== Data Paths ======
    OFFLINE_PDF_DIR: str = "./data"

    # ====== Logging ======
    LOG_LEVEL: str = "INFO"
    
    # ====== LangSmith Tracing Metrics ======
    LANGCHAIN_TRACING_V2: bool = False
    LANGCHAIN_ENDPOINT: str = "https://langchain.com"
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_PROJECT: str = "nexusmind-core"

    # 🟢 Pydantic v2 Environment Auto-Discovery Hook
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore" # Safely bypass extra keys in custom environments
    )

    # 🟢 FIELD CLEANUP VALIDATOR: Strips any unintended spaces from model strings
    @field_validator("OLLAMA_MODEL", mode="before")
    @classmethod
    def strip_model_string(cls, v: Any) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

# Instantiate the global settings object for system-wide access
settings = AppSettings()
