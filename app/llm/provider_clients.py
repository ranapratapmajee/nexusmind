# path: app/llm/provider_clients.py
import asyncio
import os

import httpx

from app.config.settings import settings

try:
    from google import genai
except ImportError:
    genai = None


def gemini_available() -> bool:
    """Verifies that both the underlying library block exists and the local API key is mapped."""
    return (
        genai is not None
        and bool(settings.llm.providers.get("gemini", {}).enabled)
        and bool(os.getenv("GEMINI_API_KEY"))
    )


def is_retryable_gemini_error(exc: Exception) -> bool:
    """Evaluates error codes to determine if a failover network route should be executed."""
    msg = str(exc).lower()
    return any(
        indicator in msg
        for indicator in [
            "503",
            "429",
            "unavailable",
            "rate limit",
            "internal server",
            "deadline",
            "timeout",
        ]
    )


async def ollama_chat(system_prompt: str, user_message: str, model_name: str) -> str:
    """Executes a non-streaming chat request natively against the local Ollama daemon service engine."""
    provider_cfg = settings.llm.providers.get("ollama", {})

    # Using the IPv4 patch we applied earlier
    base_url = "http://127.0.0.1:11434"
    url = f"{base_url.rstrip('/')}/api/chat"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "options": {"temperature": 0.2},
        "stream": False,
    }

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(60.0, connect=10.0), trust_env=False
    ) as client:
        resp = await client.post(url, json=payload)

    resp.raise_for_status()
    data = resp.json()

    return data.get("message", {}).get("content", "").strip()


async def gemini_chat(system_prompt: str, user_message: str, model_name: str) -> str:
    """Executes a synchronous thread-isolated reasoning call using Google's cloud endpoints."""
    api_key = os.getenv("GEMINI_API_KEY") or ""
    client = genai.Client(api_key=api_key)

    contents = f"{system_prompt}\n\nUser message:\n{user_message}"
    loop = asyncio.get_running_loop()

    # Explicitly configure request parameters inside our sync wrapper thread function
    def _run_sync():
        resp = client.models.generate_content(model=model_name, contents=contents)
        return resp.text or ""

    return await loop.run_in_executor(None, _run_sync)
