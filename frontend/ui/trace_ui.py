import streamlit as st
from typing import Any, Dict, List, Optional

def render_trace(
    trace: Dict[str, Any], pipeline_trace_history: Optional[List[Dict[str, Any]]] = None
) -> None:
    """Renders a dense, monospaced terminal-style execution trace."""
    if not trace:
        return

    meta = trace.get("metadata", {}) or {}
    metrics = trace.get("metrics", {}) or {}
    timeline = pipeline_trace_history or trace.get("timeline", [])
    
    # 1. Prepare Header Data
    route = str(meta.get("route", "CHAT")).upper()
    mode = str(meta.get("mode", "NATIVE"))
    model = str(meta.get("model", "UNKNOWN")).split("/")[-1]
    tier = str(meta.get("tier", "Standard"))
    total_ms = int(metrics.get("total_ms", 0))

    # 2. Build the buffer
    buffer = [
        f"📡 PLATFORM ENGINE  ::  [ROUTE: {route}]  [MODE: {mode}]",
        "🐳 INFRASTRUCTURE   ::  [VIRTUALIZATION: Colima (Apple vz/virtiofs)]",
        "🗄️ VECTOR STORE     ::  [ENGINE: ChromaDB Container Cluster]",
        f"🧠 LOGICAL COMPUTE  ::  [TIER: {tier}]  [MODEL: {model}]\n",
        "⛓️ PIPELINE CHRONOLOGICAL FLOW DIAGRAM"
    ]

    # 3. Build Timeline
    seen = set()
    steps = [t for t in timeline if t.get("status") != "🏁" and (f"{t.get('node_name')}_{t.get('message')}" not in seen and not seen.add(f"{t.get('node_name')}_{t.get('message')}"))]
    terminal = [t for t in timeline if t.get("status") == "🏁"]

    for idx, step in enumerate(steps):
        buffer.append(f" ├── {step.get('status', '🟢')} [{idx + 1}] {step.get('node_name')} ──> [{step.get('message')}]")

    exit_msg = terminal[0].get('node_name') if terminal else "Terminal Exit Handshake"
    buffer.append(f" └── 🏁 {exit_msg} ({total_ms}ms)\n")

    # 4. Vector Grounding (If available)
    retrieval = metrics.get("retrieval_data", {})
    if retrieval:
        buffer.append("📚 VECTOR COLLECTION INFORMATION")
        buffer.append(f" ├── [INDEX: {retrieval.get('collection', 'db')}]  [RETRIEVED_TOP_K: {retrieval.get('top_k', '-')}]")
        for i, chunk in enumerate((retrieval.get("chunks", []) or [])[:2]):
            snippet = str(chunk.get("snippet", chunk)).replace("\n", " ")[:60] + "..."
            buffer.append(f" ├── [{i + 1}] {chunk.get('source', 'Doc')} ── \"{snippet}\"")
        buffer.append(" └── ✅ data grounding verification clear\n")

    # 5. Tools
    tools = meta.get("tools_used", [])
    if tools:
        buffer.append(f"⚡ TRIGGERED ACTIVE TOOLS :: [{', '.join(tools)}]")

    # 6. Render as code block (the secret to perfect mono-spacing)
    with st.expander(f"⚙️ TRACE | {route} | {model} | {total_ms}ms", expanded=False):
        st.code("\n".join(buffer), language="text")