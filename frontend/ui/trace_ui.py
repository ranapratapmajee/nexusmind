# path: frontend/ui/trace_ui.py

import streamlit as st
from typing import Any, Dict, List

def render_trace(trace_logs: List[Dict[str, Any]], metrics: Dict[str, Any]) -> None:
    """
    Renders a dense, monospaced terminal-style execution trace tracking native LangGraph nodes.
    Features an isolated micro-font custom styling matrix distinct from standard chat text.
    """
    if not trace_logs:
        return

    # 1. Prepare Header and Metadata details
    total_ms = int(metrics.get("total_ms", 0))
    
    is_research = any("research" in str(log.get("node_identifier", "")).lower() for log in trace_logs)
    route = "RESEARCH" if is_research else "DIRECT_LLM"
    tier = "HIGH (Cloud Scale)" if is_research else "LOW (Local Silicon)"

    # 2. Build the ASCII buffer header matching Docker Desktop configurations
    buffer = [
        f"📡 PLATFORM ENGINE  ::  [ROUTE: {route}]",
        "🐳 INFRASTRUCTURE   ::  [VIRTUALIZATION: Docker Desktop Engine Runtime]",
        "🗄️ VECTOR STORE     ::  [ENGINE: ChromaDB Container Cluster]",
        f"🧠 LOGICAL COMPUTE  ::  [TIER: {tier}]\n",
        "⛓️ PIPELINE CHRONOLOGICAL FLOW DIAGRAM"
    ]

    # 3. Build Timeline directly off native Pydantic PipelineTraceLog fields
    seen = set()
    steps = []
    terminal_step = None

    for log in trace_logs:
        status = log.get("execution_status", "🟢")
        node = log.get("node_identifier", "UnknownNode")
        msg = log.get("telemetry_message", "")
        
        if status == "🏁":
            terminal_step = log
            continue
            
        key = f"{node}_{msg}"
        if key not in seen:
            seen.add(key)
            steps.append(log)

    for step in steps:
        step_num = step.get("step_number", 0)
        status = step.get("execution_status", "🟢")
        node = step.get("node_identifier", "Node")
        msg = step.get("telemetry_message", "")
        buffer.append(f" ├── {status} [{step_num}] {node} ──> [{msg}]")

    if terminal_step:
        exit_node = terminal_step.get("node_identifier", "Terminal Exit Handshake")
        exit_msg = terminal_step.get("telemetry_message", "")
        buffer.append(f" └── 🏁 {exit_node} ──> [{exit_msg}] ({total_ms}ms)\n")
    else:
        buffer.append(f" └── 🏁 Terminal Response Handshake (Lifecycle Complete: {total_ms}ms)\n")

    if "total_sources_found" in metrics:
        buffer.append("📚 DATA RECOVERY SUBSYSTEM")
        buffer.append(f" └── [SOURCES LOADED: {metrics.get('total_sources_found', 0)}] [RETRIEVAL COMPUTE: {metrics.get('research_gather_ms', 0)}ms]")

    # 4. Inject explicit CSS rules targeting this individual block wrapper
    # We use st.html to apply a specialized developer font layout and tiny sizing
    st.html(
        """
        <style>
            .nexa-trace-block code {
                font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
                font-size: 0.72rem !important;
                line-height: 1.35 !important;
                color: #A5B4FC !important;
                background-color: #0F172A !important;
            }
        </style>
        """
    )

    # 5. Render within an interactive container styled with our custom namespace class
    with st.expander(f"⚙️ TRACE | {route} | {total_ms}ms", expanded=False):
        st.markdown('<div class="nexa-trace-block">', unsafe_allow_html=True)
        st.code("\n".join(buffer), language="text")
        st.markdown('</div>', unsafe_allow_html=True)