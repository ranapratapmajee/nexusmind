# path: app/agents/research/research_state.py
from typing import Any, Dict, List, TypedDict


class ResearchState(TypedDict):
    """Unified context memory matrix isolated within the research agent workspace."""

    session_id: str
    question: str
    model_id: str
    mode: str
    use_web: bool

    # Processing Workspace States
    research_plan: Dict[str, Any]
    online_sources: List[Dict[str, Any]]
    retrieved_chunks: List[Dict[str, Any]]
    context_string: str

    # 🎯 FIX: Explicitly track timeline logs to prevent LangGraph state scrubbing
    subgraph_pipeline_logs: List[Dict[str, Any]]

    # Payload Returns
    answer: str
    trace: Dict[str, Any]
