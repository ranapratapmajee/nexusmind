# path: frontend/ui/formatters.py
from typing import Any, Dict, List


def format_mode_label(mode: str) -> str:
    """Converts backend entry keys directly into presentation capsule labels."""
    if mode == "deep_research":
        return "🔬 Deep Research"
    return "✨ Nexa Chat"


def get_enabled_models(model_catalog: List[str]) -> List[str]:
    """Pass-through validation to filter models. (Catalog is now a flat string list)."""
    if not model_catalog:
        return []
    return model_catalog


def get_model_label_map(enabled_models: List[str]) -> Dict[str, str]:
    """Appends environment infrastructure tags cleanly to populate selection items."""
    label_map = {}
    label_map["auto"] = "🤖 Auto Resolver"

    for m_id in enabled_models:
        if not m_id or m_id == "auto":
            continue

        lower_id = m_id.lower()
        # 🟢 Intelligently detect cloud vs local providers using flat string identifiers
        if any(cloud_p in lower_id for cloud_p in ["gemini", "google", "openai", "anthropic"]):
            label_map[m_id] = f"☁️ {m_id}"
        else:
            label_map[m_id] = f"💻 {m_id}"

    return label_map