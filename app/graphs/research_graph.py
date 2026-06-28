# filename: app/graphs/research_graph.py

import time
import logging
from typing import Dict, Any
from langgraph.graph import START, END, StateGraph
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate

from app.state_models import GlobalState
from app.llm_gateway import get_model_by_tier
from app.tools.chroma_search import search_local_vectorbase
from app.tools.web_search import search_live_web

logger = logging.getLogger("nexusmind.research_graph")

# =========================================================================
# 📝 CENTRALIZED PROMPT LAYOUT SECTION
# =========================================================================

PROMPT_CLEANSE = ChatPromptTemplate.from_messages([
    ("system", (
        "You are an expert context optimization engine inside NexusMind.\n"
        "Your task is to take the raw retrieved text materials and strip out all generic filler, "
        "high-level introductions, and conversational fluff.\n\n"
        "Rewrite the text to retain ONLY concrete architectural specifications, metrics, "
        "hardware configurations, schemas, and direct system design patterns relevant to the query."
    )),
    ("human", "User Query: {query}\n\nRaw Materials:\n{raw_text}")
])

PROMPT_SYNTHESIS = ChatPromptTemplate.from_messages([
    ("system", (
        "You are Nexa operating under SOCRATIC RESEARCH PROTOCOLS within NexusMind.\n"
        "Your mission is to synthesize the provided grounding materials into an elite, "
        "production-grade engineering analysis. Avoid conversational preambles and lead directly with your response.\n\n"
        
        "--- STRUCTURAL CONSTRAINTS ---\n"
        "1. Progressive Layering: Deconstruct the architectural design or solution systematically into progressive layers "
        "(e.g., Data/Ingestion Layer -> State/Processing Layer -> Interface/API Layer) using clear Markdown headers (##, ###).\n"
        "2. Grounded Evidence & Citations: For every design choice, trade-off, or code implementation, ground your explanation "
        "strictly in the reference material provided below. Use explicit inline citations matching the source format exactly "
        "(e.g., `[LOCAL MATERIAL]` or `[WEB SOURCE: Title | URL: ...]`). If the provided context is insufficient to fully answer an "
        "architectural detail, state this limitation clearly.\n"
        "3. Socratic Closing: End your response with a clear horizontal rule (---). Below it, create a section titled "
        "'### Socratic Discovery' containing exactly ONE sharp, targeted conceptual question. This question must challenge "
        "the developer to evaluate an edge case, scale limitation, or design bottleneck inherent to the system layout you just discussed.\n\n"
        
        "--- FOUNDATIONAL REFERENCE MATERIALS ---\n"
        "{context_string}"
    )),
    ("human", "Execute deep technical analysis for this developer query: {query}")
])

# =========================================================================
# 🎛️ RESEARCH GRAPH NODES
# =========================================================================

async def research_fetch_node(state: GlobalState) -> Dict[str, Any]:
    """Node: Aggregates vector chunks/web results and simplifies them via LLM."""
    start_time = time.perf_counter()
    queries = state.pipeline_context.get("expanded_queries") or [state.forward_query]
    
    logger.info(f"📡 [RESEARCH] Fetching and cleansing context matrix for: {queries}")
    
    # 1. Gather raw data from tools
    chunks, _, has_grounding = await search_local_vectorbase(queries)
    force_deep = state.pipeline_context.get("force_deep_research", False)
    web_sources = await search_live_web(queries) if (not has_grounding or force_deep) else []

    # 2. Compile reference strings cleanly
    context_lines = [f"[LOCAL MATERIAL]\n{c.get('document', '')}" for c in chunks] + \
                    [f"[WEB SOURCE: {s['title']} | URL: {s['url']}]\n{s['content']}" for s in web_sources]
    raw_text_payload = "\n\n---\n\n".join(context_lines)

    # 3. Use the LLM to simply cleanse the context
    if raw_text_payload.strip():
        model = get_model_by_tier(state.allocated_model_tier)
        cleansed_response = await (PROMPT_CLEANSE | model).ainvoke({
            "query": state.forward_query,
            "raw_text": raw_text_payload
        })
        formatted_string = cleansed_response.content
    else:
        formatted_string = "No reference data loaded."

    ms = int((time.perf_counter() - start_time) * 1000)
    
    return {
        "pipeline_context": {
            "retrieved_chunks": chunks,
            "online_sources": web_sources,
            "formatted_context_string": formatted_string
        },
        "performance_metrics_ms": {
            "research_gather_ms": ms,
            "total_sources_found": len(context_lines)
        },
        "messages": [
            AIMessage(content="", additional_kwargs={"status": "🔍", "telemetry": f"LLM-Cleansed context payload prepared in {ms}ms."})
        ]
    }


async def research_synthesize_node(state: GlobalState) -> Dict[str, Any]:
    """Node: Streams target data through PROMPT_SYNTHESIS to generate final response."""
    start_time = time.perf_counter()
    model = get_model_by_tier(state.allocated_model_tier)
    context_data = state.pipeline_context.get("formatted_context_string", "No reference data loaded.")
    
    logger.info("🧠 [RESEARCH] Generating response via streaming...")
    
    full_content = ""
    try:
        async for chunk in (PROMPT_SYNTHESIS | model).astream({
            "context_string": context_data,
            "query": state.forward_query
        }):
            if chunk.content:
                full_content += chunk.content
    except Exception as e:
        logger.error(f"❌ Synthesis sequence failure: {e}")
        full_content = f"❌ Technical synthesis processing sequence failed: {str(e)}"

    ms = int((time.perf_counter() - start_time) * 1000)
    return {
        "final_assistant_reply": full_content,
        "performance_metrics_ms": {"research_synthesis_ms": ms},
        "messages": [AIMessage(content=full_content)]
    }

# =========================================================================
# 🏗️ GRAPH TOPOLOGY DEFINITION
# =========================================================================

builder = StateGraph(GlobalState)
builder.add_node("research_fetch", research_fetch_node)
builder.add_node("research_synthesize", research_synthesize_node)

builder.add_edge(START, "research_fetch")
builder.add_edge("research_fetch", "research_synthesize")
builder.add_edge("research_synthesize", END)

compiled_research_graph = builder.compile()