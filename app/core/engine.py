# path: app/core/engine.py
import time
from typing import Any, Dict

from app.core.graph import get_graph


async def invoke_graph_workflow(
    session_id: str,
    message: str,
    model_id: str = "auto",
    mode: str = "chat",
) -> Dict[str, Any]:
    """
    Asynchronously invokes the compiled broker graph framework.
    Maps incoming parameters to the unified state memory fabric.
    """
    graph = get_graph()
    chat_start = time.perf_counter()

    # 🎯 CENTRALIZED DESIGN: Pre-populate the exact tracking contract structure
    initial_state = {
        "session_id": session_id,
        "user_message": message,
        "selected_model_id": model_id,
        "ui_requested_mode": mode,
        "messages": [],
        "pipeline_trace_history": [],
        "trace": {"metadata": {}, "metrics": {}, "timeline": []},
    }

    final_state: Dict[str, Any] = await graph.ainvoke(initial_state)

    reply = final_state.get("assistant_reply", "No response payload processed.")
    trace = final_state.get("trace", {}) or {}

    # Calculate overall roundtrip execution time matching our metrics layout
    if isinstance(trace, dict) and "metrics" in trace:
        if trace["metrics"].get("total_ms") is None:
            trace["metrics"]["total_ms"] = int(
                (time.perf_counter() - chat_start) * 1000
            )

    return {
        "reply": reply,
        "trace": trace,
    }
