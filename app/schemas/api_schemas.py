# path: app/schemas/api_schemas.py
from typing import Any, Dict, List, Literal, Union

from pydantic import BaseModel, Field

# Consolidate down to your 2 user-facing macro configurations
UserFacingMode = Literal["chat", "deep_research"]


class ChatRequest(BaseModel):
    """Parses raw inbound client JSON strings sent by Streamlit."""

    session_id: str
    message: str
    model_id: str = Field(default="auto", description="User-selected target engine ID.")
    mode: UserFacingMode = Field(default="chat", description="Macro entry point mode.")


class TimelineStep(BaseModel):
    """Validates an independent milestone line item inside the tree execution sequence."""

    step: int
    status: str
    node_name: str
    message: str


class ChatTrace(BaseModel):
    """
    Unified corporate APM telemetry return frame schema.
    Directly matches the metadata, metrics, and timeline structure of the global TraceTracker.
    """

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Houses route, mode, model, tier, tools_used, and operational flags.",
    )
    metrics: Dict[str, Any] = Field(
        default_factory=dict,
        description="Houses latency benchmarks and nested retrieval footprint blocks.",
    )
    timeline: List[TimelineStep] = Field(
        default_factory=list,
        description="Chronological step execution sequences for frontend terminal parsing.",
    )


class ChatResponse(BaseModel):
    """Enforces strict structural payload responses returning to frontend elements."""

    reply: str
    trace: ChatTrace = Field(default_factory=ChatTrace)


class ModelOption(BaseModel):
    """Validates configuration parameters mapped dynamically inside the catalog matrices."""

    id: str
    label: str
    provider: str
    mode: str
    tier: Union[int, str] = "Standard"
    enabled: bool = True
    status: str = "active"
    capabilities: List[str] = Field(default_factory=list)


class ChatOptionsResponse(BaseModel):
    """Broadcasts current valid execution models downstream to populate drop-down components."""

    default_model_id: str
    default_mode: UserFacingMode = "chat"
    available_modes: List[UserFacingMode] = Field(default_factory=list)
    models: List[ModelOption] = Field(default_factory=list)
