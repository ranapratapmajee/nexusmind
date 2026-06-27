import operator
from typing import Annotated, Any, Dict, List
from pydantic import BaseModel, Field

class PipelineTraceLog(BaseModel):
    step_number: int
    execution_status: str = "🟢"
    node_identifier: str
    telemetry_message: str

class GlobalState(BaseModel):
    session_id: str = "default"
    raw_user_query: str = ""
    sanitized_user_query: str = ""
    ui_requested_mode: str = "chat"
    target_pipeline_key: str = "direct_llm"
    routing_compute_tier: str = "LOW"
    dynamic_persona_mode: str = "standard_utility"
    allocated_model_id: str = "auto"
    final_assistant_reply: str = ""
    pipeline_context: Dict[str, Any] = Field(default_factory=dict)
    
    # 🟢 LangGraph automatically channels and appends to this list natively
    chronological_trace_logs: Annotated[List[PipelineTraceLog], operator.add] = Field(default_factory=list)
    performance_metrics_ms: Dict[str, int] = Field(default_factory=dict)