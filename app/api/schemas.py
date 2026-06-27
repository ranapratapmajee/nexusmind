# path: app/api/schemas.py

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.state_models import ChatPathSelection, ModelTierSelection

class ChatRequest(BaseModel):
    """Parses raw inbound client JSON parameters sent by the frontend UI."""
    session_id: str = "default"
    message: str
    
    # 🟢 Aligned with your simplified selections
    chat_selection: ChatPathSelection = ChatPathSelection.AUTO
    model_selection: ModelTierSelection = ModelTierSelection.AUTO

class ChatOptionsResponse(BaseModel):
    """Broadcasts available parameters down to Streamlit drop-down components."""
    default_chat_selection: ChatPathSelection = ChatPathSelection.AUTO
    default_model_selection: ModelTierSelection = ModelTierSelection.AUTO
    available_chat_paths: List[str] = Field(default_factory=list)
    available_model_tiers: List[str] = Field(default_factory=list)
