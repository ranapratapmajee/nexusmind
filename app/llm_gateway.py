# path: app/llm_gateway.py

import time
import logging
import httpx
from typing import Any, Dict
from app.settings import settings

logger = logging.getLogger("nexusmind.llm_gateway")

try:
    from google import genai
except ImportError:
    genai = None

# =========================================================================
# 📝 SYSTEM PROMPT TEMPLATES (Flat & Grounded)
# =========================================================================

SYSTEM_BASE = (
    f"You are {settings.bot_name}, an optimized AI/ML engineering assistant running inside NexusMind.\n"
    "Mandates:\n"
    "1. Technical Accuracy: Provide rigorous breakdowns. Never hallucinate schemas.\n"
    "2. Architectural Grounding: When explaining data processing, orchestration loops, or RAG frameworks, explicitly retain structural design terms like 'chunk', 'embeddings', 'state', or 'StateGraph' exactly as presented.\n"
    "3. Formatting: Use Markdown for prose/code, and LaTeX ($...$ or $$...$$) ONLY for formal math equations.\n"
    "4. Governance: Maintain any '[..._REDACTED]' tokens exactly as presented."
)

SOCRATIC_PROFESSOR_ADDENDUM = """
### ROLE: SOCRATIC PROFESSOR PERSONA
You are providing direct, personalized research mentorship.
1. Deconstruct complex system designs into progressive, digestible conceptual layers.
2. Explicitly cite underlying sources using compact inline markers.
3. Conclude your response with exactly one targeted question to challenge comprehension.
"""

def get_system_prompt(persona_mode: str) -> str:
    """Combines prompt layers cleanly based on the assigned state persona."""
    if persona_mode == "socratic_professor":
        return f"{SYSTEM_BASE}\n\n{SOCRATIC_PROFESSOR_ADDENDUM}"
    return SYSTEM_BASE

# =========================================================================
# 🚀 CORE ATOMIC PROVIDER CLIENT CONNS
# =========================================================================

async def call_local_ollama(system_prompt: str, user_message: str, model_id: str) -> str:
    """Executes a direct non-streaming request against the local Ollama service."""
    url = f"{settings.OLLAMA_BASE_URL.rstrip('/')}/api/chat"
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "options": {"temperature": 0.2},
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=httpx.Timeout(60.0, connect=10.0), trust_env=False) as client:
        resp = await client.post(url, json=payload)
        resp.raise_for_status()
        return resp.json().get("message", {}).get("content", "").strip()


async def call_cloud_gemini(system_prompt: str, user_message: str, model_id: str) -> str:
    """Executes a text generation request using the official cloud Gemini GenAI client."""
    if not genai or not settings.GEMINI_API_KEY:
        raise RuntimeError("Google GenAI client library missing or GEMINI_API_KEY unmapped in environment.")
    
    client = genai.Client(api_key=settings.GEMINI_API_KEY)
    combined_contents = f"{system_prompt}\n\nUser Message:\n{user_message}"
    
    import asyncio
    loop = asyncio.get_running_loop()
    resp = await loop.run_in_executor(None, lambda: client.models.generate_content(model=model_id, contents=combined_contents))
    return resp.text or ""

# =========================================================================
# 🎛️ UNIFIED GENERATION GATEWAY COMPOSER
# =========================================================================

async def generate_with_meta(
    task_type: str, user_message: str, model_id: str = "auto", persona_mode: str = "standard_utility"
) -> Dict[str, Any]:
    """Unified high-performance gateway execution path accepting explicit persona tags."""
    target_model = model_id if model_id != "auto" else settings.OLLAMA_MODEL
    provider = "gemini" if "gemini" in target_model.lower() else "ollama"
    
    # Intelligently sync state routing values
    resolved_persona = "socratic_professor" if task_type == "research_synthesis" or persona_mode == "socratic_professor" else "standard_utility"
    system_prompt = get_system_prompt(resolved_persona)

    if provider == "gemini":
        try:
            text = await call_cloud_gemini(system_prompt, user_message, target_model)
            return {"text": text, "provider": "gemini", "model": target_model}
        except Exception as e:
            logger.warning(f"Cloud API failure. Falling back to local hardware. Log: {e}")
            provider = "ollama"
            target_model = settings.OLLAMA_MODEL

    text = await call_local_ollama(system_prompt, user_message, target_model)
    return {"text": text, "provider": provider, "model": target_model}


async def generate(task_type: str, user_message: str, model_id: str = "auto", persona_mode: str = "standard_utility") -> str:
    """Helper shortcut returning raw plaintext string payloads."""
    res = await generate_with_meta(task_type, user_message, model_id, persona_mode)
    return res["text"]