import os
import re
import tomllib
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field

# 🎯 Establish Absolute Project Root for SSOT Lookups
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def get_project_version() -> str:
    """Extracts the global application version directly from pyproject.toml SSOT."""
    try:
        toml_path = PROJECT_ROOT / "pyproject.toml"
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.0.0")
    except Exception:
        return "0.0.0"


class AppSection(BaseModel):
    name: str
    bot_name: str
    description: str
    # Dynamically injects version from pyproject.toml at instantiation
    version: str = Field(default_factory=get_project_version)


class ServerSection(BaseModel):
    host: str
    port: int
    log_level: str


class FrontendSection(BaseModel):
    host: str
    port: int


class ProviderConfig(BaseModel):
    enabled: bool
    base_url: Optional[str] = None
    primary_model: Optional[str] = None
    planner_model: Optional[str] = None
    small_reasoning_model: Optional[str] = None
    model: Optional[str] = None
    default_model: Optional[str] = None


class LlmSection(BaseModel):
    default_tier: int
    default_model_id: str
    providers: Dict[str, ProviderConfig]
    available_models: List[Dict[str, Any]] = Field(default_factory=list)
    routing_rules: Dict[str, Any] = Field(default_factory=dict)


class ChromaSection(BaseModel):
    host: str
    port: int
    collection_prefix: str
    upsert_batch_size: int


class VectorstoresSection(BaseModel):
    chroma: ChromaSection
    collections: Dict[str, str]


class ResearchSection(BaseModel):
    offline_pdf_dir_env: str
    top_k_retrieval: int
    max_sources_online: int


class RagSection(BaseModel):
    chunk_size: int
    chunk_overlap: int
    embedding_model: str = "nomic-embed-text"


class NexusSettings(BaseModel):
    """Parses combined environmental properties securely into an immutable schema layer."""

    app: AppSection
    server: ServerSection
    frontend: FrontendSection
    llm: LlmSection
    vectorstores: VectorstoresSection
    research: ResearchSection
    rag: RagSection

    @property
    def routing(self) -> Any:
        """Dynamic alias bridge providing backward-compatibility for legacy router code layers."""

        class RoutingBridge:
            def __init__(self, llm_sec: LlmSection):
                self.default_model = llm_sec.default_model_id
                self.rules = llm_sec.routing_rules
                self.default_mode = "chat"

        return RoutingBridge(self.llm)

    @property
    def models_catalog(self) -> List[Dict[str, Any]]:
        """Maps available backend structural model dictionary specs for options endpoints."""
        return self.llm.available_models

    @classmethod
    def load_and_interpolate(cls) -> "NexusSettings":
        """Replaces string placeholder structures with environment variables cleanly."""
        env_path = Path(".env")
        if env_path.exists():
            with open(env_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, val = line.split("=", 1)
                        key = key.strip()
                        val = val.split("#")[0].strip().strip("'").strip('"')
                        if key not in os.environ:
                            os.environ[key] = val

        config_env_path = os.getenv("NEXUS_CONFIG_PATH")
        target_path = None

        paths_to_verify = [
            Path(config_env_path) if config_env_path else None,
            Path("backend/app/config/config.yaml"),
            Path("app/config/config.yaml"),
            Path(__file__).parent / "config.yaml",
        ]

        for p in paths_to_verify:
            if p and p.exists() and p.is_file():
                target_path = p
                break

        if not target_path:
            raise FileNotFoundError(
                "NexusMind config.yaml could not be resolved across standard target boundaries."
            )

        with open(target_path, "r", encoding="utf-8") as f:
            raw_content = f.read()

        def replace_env_var(match: re.Match) -> str:
            var_name = match.group(1)
            fallback_map = {
                "API_PORT": "8001",
                "FRONTEND_PORT": "8501",
                "CHROMA_PORT": "8000",
            }
            return os.getenv(var_name, fallback_map.get(var_name, match.group(0)))

        interpolated_content = re.sub(r"\$\{(\w+)\}", replace_env_var, raw_content)
        yaml_data = yaml.safe_load(interpolated_content)

        return cls(**yaml_data)


# 🎯 THE RECURSION SHIELD: Lazy singleton loading prevents boot-time import loops
_cached_settings: Optional[NexusSettings] = None


def get_settings() -> NexusSettings:
    """Provides global access to settings, instantiating them safely on demand."""
    global _cached_settings
    if _cached_settings is None:
        _cached_settings = NexusSettings.load_and_interpolate()
    return _cached_settings


# Proxy class to allow other files to use `settings.property` transparently without refactoring code
class SettingsProxy:
    def __getattr__(self, name: str) -> Any:
        return getattr(get_settings(), name)


settings = SettingsProxy()
