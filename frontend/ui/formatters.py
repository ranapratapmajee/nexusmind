# path: frontend/ui/formatters.py
from typing import Any, Dict, List


def format_mode_label(mode: str) -> str:
    """Converts backend entry keys directly into presentation capsule labels."""
    if mode == "deep_research":
        return "🔬 Deep Research"
    return "✨ Nexa Chat"


def get_enabled_models(model_catalog: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Safely filters active engines out of your centralized discovery catalog arrays."""
    if not model_catalog:
        return []
    return [m for m in model_catalog if m.get("enabled", True)]


def get_model_label_map(enabled_models: List[Dict[str, Any]]) -> Dict[str, str]:
    """Appends environment infrastructure tags cleanly to populate selection items."""
    label_map = {}
    label_map["auto"] = "🤖 Auto Resolver"

    for model in enabled_models:
        m_id = model.get("id")
        if not m_id or m_id == "auto":
            continue

        provider = model.get("provider", "").lower()
        label = model.get("label", m_id)

        # Dynamic tags inform you instantly whether compute layers run locally or in the cloud
        if provider in ["gemini", "google", "openai", "anthropic"]:
            label_map[m_id] = f"☁️ {label}"
        else:
            label_map[m_id] = f"💻 {label}"

    return label_map
