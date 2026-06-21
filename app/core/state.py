# path: app/core/state.py
import copy
import operator
from typing import Annotated, Any, Dict, List, Optional, TypedDict


class TelemetryTrace(TypedDict, total=False):
    """Industry-standard structured trace execution telemetry framework."""

    metadata: Dict[str, Any]
    metrics: Dict[str, Any]
    timeline: List[Dict[str, Any]]


def merge_trace(current: Any, update: Any) -> Any:
    """
    State Channel Reducer for Telemetry Engine.
    Explicitly overrides LangGraph's default validation behavior by forcing
    an absolute replacement write pass to prevent async serialization deadlocks.
    """
    if not update:
        return current if current else {"metadata": {}, "metrics": {}, "timeline": []}
    return update


class NexusState(TypedDict):
    """The unified runtime memory fabric for NexusMind."""

    session_id: str
    selected_model_id: str
    ui_requested_mode: str
    message: str
    user_message: str
    messages: Annotated[List[Dict[str, Any]], operator.add]
    current_intent_route: str
    persona_mode: str
    governance_passed: bool
    security_flags: List[str]
    next_step: str
    retrieved_context_chunks: List[str]
    expanded_queries: List[str]
    assistant_reply: str
    pipeline_trace_history: Annotated[List[Dict[str, Any]], operator.add]
    trace: Annotated[TelemetryTrace, merge_trace]


class TraceTracker:
    """
    Global Telemetry Engine for NexusMind.
    Schema-agnostic, decentralized ledger manager capable of tracking execution
    contexts across distinct subgraphs, tools, and background worker threads.
    """

    def __init__(self, trace_state: Optional[Dict[str, Any]] = None) -> None:
        # 🎯 FIX: Deepcopy severs the memory link preventing the infinite loop!
        self._state: Dict[str, Any] = copy.deepcopy(trace_state) if trace_state else {}

        if "metadata" not in self._state:
            self._state["metadata"] = {}
        if "metrics" not in self._state:
            self._state["metrics"] = {}
        if "timeline" not in self._state:
            self._state["timeline"] = []

    @classmethod
    def from_state(cls, state: Dict[str, Any]) -> "TraceTracker":
        """Factory method to instantly bind to any LangGraph execution state map."""
        return cls(state.get("trace", {}) or {})

    @property
    def compiled_trace(self) -> Dict[str, Any]:
        """
        Returns a clean snapshot of the structured telemetry data payload.
        Explicitly isolates the internal tree to remain safe from LangGraph reducer loops.
        """
        return {
            "metadata": dict(self._state["metadata"]),
            "metrics": dict(self._state["metrics"]),
            "timeline": list(self._state["timeline"]),
        }

    @property
    def timeline(self) -> List[Dict[str, Any]]:
        """Direct access to the step execution array list."""
        return self._state["timeline"]

    def set_metadata(self, **kwargs: Any) -> "TraceTracker":
        """Dynamically injects or overrides global environment metadata properties from anywhere."""
        for key, val in kwargs.items():
            if val is not None:
                if key == "tools_used":
                    current_tools = list(self._state["metadata"].get("tools_used", []))
                    self._state["metadata"]["tools_used"] = list(
                        set(current_tools + list(val))
                    )
                else:
                    self._state["metadata"][key] = val
        return self

    def set_metric(self, key: str, value: Any) -> "TraceTracker":
        """Logs precision metrics, performance benchmarks, or data sub-payloads."""
        self._state["metrics"][key] = value
        return self

    def log_step(
        self, activity_name: str, status_msg: str, status_icon: str = "🟢"
    ) -> "TraceTracker":
        """Appends an execution line milestone to the active runtime sequence."""
        timeline = self._state["timeline"]

        # Pull out terminal elements if adding intermediate nodes late
        terminal = (
            timeline.pop()
            if (timeline and timeline[-1].get("status") == "🏁")
            else None
        )

        timeline.append(
            {
                "step": len(timeline) + 1,
                "status": status_icon,
                "node_name": str(activity_name),
                "message": str(status_msg),
            }
        )

        if terminal:
            terminal["step"] = len(timeline) + 1
            timeline.append(terminal)

        return self

    def log_external_sequence(
        self, sequence_logs: List[Dict[str, Any]]
    ) -> "TraceTracker":
        """Stitches foreign log list histories cleanly onto the primary tracker timeline."""
        # 🎯 FIX: Wrap sequence_logs in list() to freeze a temporary copy for the loop
        for log in list(sequence_logs):
            msg = log.get("message", "Processed successfully")
            icon = log.get("status")

            if not icon:
                icon = (
                    "🟡"
                    if any(x in msg.lower() for x in ["fail", "miss", "error"])
                    else "🟢"
                )

            self.log_step(
                activity_name=log.get(
                    "node_name", log.get("activity_name", "Sub-Activity")
                ),
                status_msg=msg,
                status_icon=icon,
            )
        return self

    def close_telemetry(self, total_runtime_ms: int) -> List[Dict[str, Any]]:
        """Caps overall execution loops and appends the final application layer anchor."""
        self.set_metric("total_ms", total_runtime_ms)
        timeline = self._state["timeline"]

        if not any(item.get("status") == "🏁" for item in timeline):
            timeline.append(
                {
                    "step": len(timeline) + 1,
                    "status": "🏁",
                    "node_name": "Terminal Exit Handshake",
                    "message": f"Execution lifecycle completed in {total_runtime_ms}ms",
                }
            )
        return timeline
