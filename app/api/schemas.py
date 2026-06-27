# path: app/api/schemas.py

from typing import Any, Dict, List, Literal
from pydantic import BaseModel, Field
from app.state_models import PipelineTraceLog  # 🟢 Aligned import location pointer

UserFacingMode = Literal["chat", "deep_research"]

class ChatRequest(BaseModel):
    """Parses raw inbound client JSON strings sent by the user interface."""
    session_id: str = "default"
    message: str
    model_id: str = "auto"
    mode: UserFacingMode = "chat"

class ChatResponse(BaseModel):
    """Enforces execution response contracts returning downstream to frontend elements."""
    reply: str
    trace_logs: List[PipelineTraceLog] = Field(default_factory=list)
    metrics: Dict[str, int] = Field(default_factory=dict)

class ChatOptionsResponse(BaseModel):
    """Broadcasts available model parameters directly down to UI drop-down selectors."""
    default_model_id: str
    default_mode: UserFacingMode = "chat"
    available_modes: List[UserFacingMode] = Field(default_factory=list)
    available_models: List[str] = Field(default_factory=list)