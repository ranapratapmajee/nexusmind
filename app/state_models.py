import operator
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# =========================================================================
# OPERATIONAL UNIFIED ENUMS
# =========================================================================

class ChatPathSelection(str, Enum):
    NEXA_CHAT = "NEXA_CHAT"
    RESEARCH = "RESEARCH"

class ModelTierSelection(str, Enum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"

class ChatRequest(BaseModel):
    """Parses raw inbound client JSON parameters sent by the frontend UI."""
    session_id: str = "default"
    message: str
    
    # Defaults set to NEXA_CHAT and LOCAL if frontend does not provide them
    chat_selection: Optional[ChatPathSelection] = ChatPathSelection.NEXA_CHAT
    model_selection: Optional[ModelTierSelection] = ModelTierSelection.LOCAL

class ChatOptionsResponse(BaseModel):
    """Broadcasts available parameters down to Streamlit drop-down components."""
    default_chat_selection: Optional[ChatPathSelection] = ChatPathSelection.NEXA_CHAT
    default_model_selection: Optional[ModelTierSelection] = ModelTierSelection.LOCAL
    available_chat_paths: List[Dict[str, str]] = Field(default_factory=list)
    available_model_tiers: List[Dict[str, str]] = Field(default_factory=list)

# =========================================================================
# 🧠 STATE GRAPH SCHEMA STRUCTURE
# =========================================================================

class GlobalState(BaseModel):
    """🌊 Pure, high-density data synchronization pipeline state layer."""
    raw_user_query: str = ""
    forward_query: str = ""
    
    user_selected_path: Optional[ChatPathSelection] = ChatPathSelection.NEXA_CHAT
    user_selected_model: Optional[ModelTierSelection] = ModelTierSelection.LOCAL
    
    target_router_path: ChatPathSelection = ChatPathSelection.NEXA_CHAT
    allocated_model_tier: ModelTierSelection = ModelTierSelection.LOCAL
    
    guardrails_passed: bool = True
    final_assistant_reply: str = ""
    
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
    pipeline_context: Annotated[Dict[str, Any], operator.or_] = Field(default_factory=dict)
    performance_metrics_ms: Annotated[Dict[str, int], operator.or_] = Field(default_factory=dict)