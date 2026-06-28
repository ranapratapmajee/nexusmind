import operator
from enum import Enum
from typing import Annotated, Any, Dict, List, Optional
from pydantic import BaseModel, Field
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages

# =========================================================================
# 🎛️ 1. OPERATIONAL UNIFIED ENUMS
# =========================================================================

class ChatPathSelection(str, Enum):
    NEXA_CHAT = "NEXA_CHAT"
    RESEARCH = "RESEARCH"

class ModelTierSelection(str, Enum):
    LOCAL = "LOCAL"
    CLOUD = "CLOUD"

# =========================================================================
# 🧠 2. STATE GRAPH SCHEMA STRUCTURE
# =========================================================================

class GlobalState(BaseModel):
    """🌊 Pure, high-density data synchronization pipeline state layer."""
    raw_user_query: str = ""
    forward_query: str = ""
    
    # 📥 User Explicit Selections (Overrides from Frontend)
    user_selected_path: Optional[ChatPathSelection] = None
    user_selected_model: Optional[ModelTierSelection] = None
    
    # ⚙️ Final Internal Orchestration Targets
    # Defaults applied exactly per your requirements.
    target_pipeline_key: ChatPathSelection = ChatPathSelection.NEXA_CHAT
    allocated_model_tier: ModelTierSelection = ModelTierSelection.LOCAL
    
    # SAFETY HALT CONTROL
    guardrails_passed: bool = True
    final_assistant_reply: str = ""
    
    # LangGraph Automatic Channel Merging Channels
    messages: Annotated[List[AnyMessage], add_messages] = Field(default_factory=list)
    pipeline_context: Annotated[Dict[str, Any], operator.or_] = Field(default_factory=dict)
    performance_metrics_ms: Annotated[Dict[str, int], operator.or_] = Field(default_factory=dict)