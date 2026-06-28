from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.state_models import ChatPathSelection, ModelTierSelection

class ChatRequest(BaseModel):
    """Parses raw inbound client JSON parameters sent by the frontend UI."""
    session_id: str = "default"
    message: str
    
    # 🟢 None means "Auto" on the UI layer; the backend pipeline will resolve defaults cleanly.
    chat_selection: Optional[ChatPathSelection] = None
    model_selection: Optional[ModelTierSelection] = None

class ChatOptionsResponse(BaseModel):
    """Broadcasts available parameters down to Streamlit drop-down components."""
    default_chat_selection: Optional[ChatPathSelection] = None
    default_model_selection: Optional[ModelTierSelection] = None
    available_chat_paths: List[Dict[str, str]] = Field(default_factory=list)
    available_model_tiers: List[Dict[str, str]] = Field(default_factory=list)