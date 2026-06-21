# path: app/llm/gateway.py
import time
from typing import Any, Dict, Optional

from app.config.settings import settings
from app.core.state import TraceTracker  # 🎯 Centralized Trace Integration
from app.llm.prompt_builder import build_dynamic_system_prompt
from app.llm.provider_clients import (
    gemini_available,
    gemini_chat,
    is_retryable_gemini_error,
    ollama_chat,
)


def _resolve_model_record(model_id: str) -> Dict[str, Any]:
    """Helper method to look up a model configuration inside our settings block."""
    catalog = settings.llm.available_models

    target_id = model_id if model_id != "auto" else settings.llm.default_model_id
    if target_id == "auto":
        return {
            "id": "qwen2.5-coder:3b-instruct",
            "provider": "ollama",
            "tier": "Standard",
        }

    for m in catalog:
        if m.get("id") == target_id:
            return m

    return {"id": target_id, "provider": "ollama", "tier": "Standard"}


async def generate_with_meta(
    task_type: str,
    user_message: str,
    importance: str = "low",
    model_id: str = "auto",
    use_web: bool = True,
    persona_mode: str = "standard_utility",
    tracker: Optional[TraceTracker] = None,  # 🎯 Centralized stateful ledger linkage
) -> Dict[str, Any]:
    """
    Unified high-performance runtime interface executing client LLM network tasks.
    Gracefully transitions processing layers to local tiers upon connection loss
    and updates centralized telemetry registers seamlessly mid-flight.
    """
    model_meta = _resolve_model_record(model_id)
    provider = model_meta.get("provider", "ollama")
    resolved_name = model_meta.get("id")

    raw_tier = model_meta.get("tier", "Standard")
    is_advanced = raw_tier in [1, "1", "Advanced", "Advanced Reasoning"]
    tier_label = "Advanced Reasoning" if is_advanced else "Standard Stream"

    system_prompt = build_dynamic_system_prompt(persona_mode)
    fallback_used = False
    fallback_reason = None

    start_time = time.perf_counter()

    # Route 1: Target Cloud Provider Engine (with automated failover route security)
    if provider in ["gemini", "google"] and gemini_available():
        try:
            if tracker:
                tracker.log_step(
                    "LLM Compute Core",
                    f"Dispatching payload to cloud network gateway ({resolved_name})",
                )

            text = await gemini_chat(system_prompt, user_message, resolved_name)
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)

            # Update centralized telemetry logs immediately upon success
            if tracker:
                tracker.set_metadata(model=resolved_name, tier=tier_label)
                tracker.set_metric(f"llm_{task_type}_ms", elapsed_ms)

            return {
                "text": text,
                "provider": "gemini",
                "model": resolved_name,
                "tier": tier_label,
                "fallback_used": False,
            }
        except Exception as e:
            # Evaluate if the error is a systemic retryable issue before falling back
            if is_retryable_gemini_error(e):
                fallback_used = True
                fallback_reason = str(e)
                provider = "ollama"
                resolved_name = "qwen2.5-coder:3b-instruct"

                if tracker:
                    tracker.log_step(
                        "LLM Compute Core Failover",
                        f"Cloud API degradation detected. Redirecting to local hardware tier. Log: {fallback_reason[:60]}...",
                        status_icon="🟡",
                    )
            else:
                # If it's a syntax or validation error, let it bubble up instantly to prevent silent stalls
                if tracker:
                    tracker.log_step(
                        "LLM Compute Core Fault",
                        f"Cloud API schema exception: {str(e)[:80]}",
                        status_icon="🔴",
                    )
                raise e

    # Route 2: Target Local Engine Execution Stream
    try:
        if tracker and fallback_used:
            tracker.log_step(
                "LLM Compute Core Fallback",
                f"Executing target instruction block via local model ({resolved_name})",
            )

        # 🎯 ALIGNED: Safely invoke native async provider chat without deadlocking
        text = await ollama_chat(system_prompt, user_message, resolved_name)
        elapsed_ms = int((time.perf_counter() - start_time) * 1000)

        # Sync final runtime execution states natively using decoupled fluent setters
        if tracker:
            tracker.set_metadata(
                model=resolved_name,
                tier="Standard Stream" if not fallback_used else "Fallback Tier",
            )
            tracker.set_metric(f"llm_{task_type}_ms", elapsed_ms)

        return {
            "text": text,
            "provider": "ollama",
            "model": resolved_name,
            "tier": "Standard Stream"
            if not fallback_used
            else f"Fallback Stream ({tier_label} Down)",
            "fallback_used": fallback_used,
            "fallback_reason": fallback_reason,
        }
    except Exception as e:
        if tracker:
            tracker.log_step(
                "LLM Compute Core Fault",
                f"Fatal execution failure on local model node: {str(e)[:60]}",
                status_icon="🔴",
            )

        return {
            "text": f"Critical LLM Layer Fault: Unable to reach your local execution server daemon. Log: `{e}`",
            "provider": "none",
            "model": "none",
            "tier": "none",
            "fallback_used": True,
        }


async def generate(
    task_type: str, user_message: str, importance: str = "low", model_id: str = "auto"
) -> str:
    """Helper shortcut returning raw plaintext string payloads for utility graph nodes."""
    res = await generate_with_meta(task_type, user_message, importance, model_id)
    return res["text"]


async def llm_chat_as_nexa(
    user_message: str, session_id: str, model_id: str = "auto", mode: str = "chat"
) -> str:
    """Direct conversational workspace adapter connecting straight to frontend interface calls."""
    res = await generate_with_meta(
        task_type="generic_chat",
        user_message=user_message,
        model_id=model_id,
        persona_mode=mode,
    )
    return res["text"]
