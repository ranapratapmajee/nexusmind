# path: app/llm_gateway.py

import logging
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_google_genai import ChatGoogleGenerativeAI
from app.settings import settings
from app.state_models import ModelTierSelection

logger = logging.getLogger("nexusmind.llm_gateway")

def get_local_model() -> BaseChatModel:
    """Initializes standard local hardware client with zero timeout boundaries."""
    return ChatOllama(
        base_url=settings.OLLAMA_BASE_URL,
        model=settings.OLLAMA_MODEL,
        temperature=0.2,
        num_predict=4096,
        timeout=None  # 🟢 UNLIMITED TIMEOUT BOUNDARY: Local models can think indefinitely
    )

def get_cloud_model() -> BaseChatModel:
    """Initializes cloud client with automatic local hardware backup fallback."""
    api_key = settings.GEMINI_API_KEY or settings.GOOGLE_API_KEY
    if not api_key:
        logger.warning("Cloud API credentials missing. Falling back to local silicon client.")
        return get_local_model()
        
    cloud_model = ChatGoogleGenerativeAI(
        api_key=api_key,
        model=settings.GEMINI_MODEL,
        temperature=0.2,
        timeout=None  # 🟢 UNLIMITED TIMEOUT BOUNDARY: Prevents API gateway network drops
    )
    return cloud_model.with_fallbacks([get_local_model()])

def get_model_by_tier(tier: ModelTierSelection) -> BaseChatModel:
    """Maps the state's allocated model tier selection enum directly to its client."""
    if tier == ModelTierSelection.CLOUD:
        return get_cloud_model()
    return get_local_model()
