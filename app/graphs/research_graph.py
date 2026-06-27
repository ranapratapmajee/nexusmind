# path: app/graphs/research_graph.py

import time
from typing import Dict, Any
from langgraph.graph import START, END, StateGraph
from app.state_models import GlobalState, PipelineTraceLog
from app.llm_gateway import generate_with_meta
from app.tools.chroma_search import search_local_vectorbase
from app.tools.web_search import search_live_web

# =========================================================================
# 🎛️ RESEARCH GRAPH NODES
# =========================================================================

async def gather_sources_node(state: GlobalState) -> Dict[str, Any]:
    """Node: Aggregates vector chunks and web lookups concurrently using tools."""
    start_time = time.perf_counter()
    new_logs = []
    
    # Dynamically pick up the current log count from the main state
    base_step = len(state.chronological_trace_logs)
    
    queries = state.pipeline_context.get("expanded_queries") or [state.sanitized_user_query]
    new_logs.append(PipelineTraceLog(step_number=base_step + 1, node_identifier="Research Core", telemetry_message="Invoking atomic search tools across variations."))

    chunks, best_dist, has_grounding = await search_local_vectorbase(queries)
    if has_grounding:
        new_logs.append(PipelineTraceLog(step_number=base_step + 2, node_identifier="ChromaDB Engine", telemetry_message=f"Grounding match confirmed across vectors (Dist: {best_dist:.2f})"))
    else:
        new_logs.append(PipelineTraceLog(step_number=base_step + 2, execution_status="🟡", node_identifier="ChromaDB Engine", telemetry_message="Local vector store proximity fell below threshold variables."))

    web_sources = []
    if not has_grounding or state.ui_requested_mode == "deep_research":
        new_logs.append(PipelineTraceLog(step_number=base_step + 3, node_identifier="Web Scraper", telemetry_message="Executing live web lookup fallback transformations."))
        web_sources = await search_live_web(queries)

    context_lines = [f"[LOCAL FILE MATERIAL]\n{c.get('document', '')}" for c in chunks] + \
                    [f"[WEB MATERIAL: {s['title']} | URL: {s['url']}]\n{s['content']}" for s in web_sources]

    updated_context = {
        **state.pipeline_context,
        "retrieved_chunks": chunks,
        "online_sources": web_sources,
        "formatted_context_string": "\n\n---\n\n".join(context_lines)
    }

    updated_metrics = {
        **state.performance_metrics_ms,
        "research_gather_ms": int((time.perf_counter() - start_time) * 1000),
        "total_sources_found": len(chunks) + len(web_sources)
    }

    return {
        "pipeline_context": updated_context,
        "chronological_trace_logs": new_logs,
        "performance_metrics_ms": updated_metrics
    }


async def synthesize_research_node(state: GlobalState) -> Dict[str, Any]:
    """Node: Synthesizes gathered data into a citation-tracked markdown response."""
    start_time = time.perf_counter()
    
    # Pick up current log length dynamically so step sequence never breaks
    base_step = len(state.chronological_trace_logs)
    
    new_logs = [
        PipelineTraceLog(step_number=base_step + 1, node_identifier="Synthesis Engine", telemetry_message=f"Generating response via [{state.allocated_model_id}].")
    ]

    prompt = (
        f"Persona Settings: {state.dynamic_persona_mode}\n"
        f"User Query Objective: {state.sanitized_user_query}\n\n"
        f"Foundational Source Context Block:\n{state.pipeline_context.get('formatted_context_string', 'No reference data loaded.')}\n\n"
        "Synthesize the provided materials into a clean technical explanation. Include embedded citations."
    )

    try:
        response = await generate_with_meta(
            task_type="research_synthesis",
            user_message=prompt,
            model_id=state.allocated_model_id
        )
        reply = response.get("text", "").strip()
    except Exception as e:
        reply = f"❌ Technical synthesis failed: {str(e)}"

    new_logs.append(PipelineTraceLog(step_number=base_step + 2, node_identifier="Research Core", telemetry_message="Deep analysis complete."))

    updated_metrics = {
        **state.performance_metrics_ms,
        "research_synthesis_ms": int((time.perf_counter() - start_time) * 1000)
    }

    return {
        "final_assistant_reply": reply,
        "chronological_trace_logs": new_logs,
        "performance_metrics_ms": updated_metrics
    }

# =========================================================================
# 🏗️ GRAPH TOPOLOGY DEFINITION
# =========================================================================

builder = StateGraph(GlobalState)
builder.add_node("gather_sources", gather_sources_node)
builder.add_node("synthesize_research", synthesize_research_node)

builder.add_edge(START, "gather_sources")
builder.add_edge("gather_sources", "synthesize_research")
builder.add_edge("synthesize_research", END)

# Expose compiled subgraph instance cleanly to app/core_graph.py
compiled_research_graph = builder.compile()