# path: app/chat/chat_app.py
from typing import Any, Dict

from app.config.settings import settings
from app.core.engine import invoke_graph_workflow
from app.schemas.api_schemas import (
    ChatOptionsResponse,
    ChatRequest,
    ChatResponse,
    ChatTrace,
    ModelOption,
)


def build_chat_options_response() -> ChatOptionsResponse:
    """Dynamically broadcasts type-safe model metadata frameworks straight down to frontend pickers."""
    available_models = settings.llm.available_models

    return ChatOptionsResponse(
        default_model_id=settings.llm.default_model_id,
        default_mode="chat",
        available_modes=[
            "chat",
            "deep_research",
        ],
        models=[
            ModelOption(
                id=m["id"],
                label=m["label"],
                provider=m["provider"],
                mode=m.get("mode", "unknown"),
                tier=m.get("tier", "Standard"),
                enabled=m.get("enabled", True),
                status=m.get("status", "active"),
                capabilities=m.get("capabilities", []),
            )
            for m in available_models
            if m.get("enabled", True)
        ],
    )


def _normalize_response_trace(result: Dict[str, Any], req: ChatRequest) -> ChatTrace:
    """Transforms unified schema-agnostic tracker dictionaries into type-safe ChatTrace responses."""
    # Pull out the dynamic trace package populated across backend execution nodes
    raw_trace = result.get("trace", {}) or {}

    # Initialize standard type-safe trace container matching metadata, metrics, & timeline registers
    return ChatTrace(
        metadata=raw_trace.get("metadata", {}),
        metrics=raw_trace.get("metrics", {}),
        timeline=raw_trace.get("timeline", []),
    )


async def handle_chat_request(req: ChatRequest) -> ChatResponse:
    """Directly invokes your LangGraph orchestration engine broker stream thread."""
    result = await invoke_graph_workflow(
        session_id=req.session_id,
        message=req.message,
        model_id=req.model_id,
        mode=req.mode,
    )

    return ChatResponse(
        reply=result.get("reply", "No response payload processed."),
        trace=_normalize_response_trace(result, req),
    )
