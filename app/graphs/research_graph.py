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

# Obtain the exact logger mapping matching your project structure
logger = logging.getLogger("nexusmind.research_graph")

# =========================================================================
# 📝 CENTRALIZED PROMPT LAYOUT SECTION
# =========================================================================

PROMPT_SYNTHESIS = ChatPromptTemplate.from_messages([
    ("system", (
        "You are a specialized technical analysis agent. Synthesize the provided reference "
        "materials into a clean engineering explanation. Explicitly retain structural terms. "
        "Include embedded inline citations matching the source formats exactly.\n\n"
        "Foundational Reference Materials:\n{context_string}"
    )),
    ("human", "{query}")
])

# =========================================================================
# 🎛️ RESEARCH GRAPH NODES
# =========================================================================

async def gather_sources_node(state: GlobalState) -> Dict[str, Any]:
    """Node: Aggregates local vector chunks and live web lookups dynamically."""
    start_time = time.perf_counter()
    
    # Safely look for search term queries using your renamed forward_query fallback variable
    queries = state.pipeline_context.get("expanded_queries") or [state.forward_query]
    
    logger.info("📡 [RESEARCH SUBGRAPH] Initializing Parallel Retrieval Matrix...")
    logger.info(f"   └── 🔍 Processing Query Variations: {queries}")
    
    # 1. Execute local vector lookup
    logger.info("   🗄️ Invoking ChromaDB Vector Store client...")
    chunks, best_dist, has_grounding = await search_local_vectorbase(queries)
    grounding_status = "confirmed" if has_grounding else "below threshold"
    
    logger.info(f"   └── 📥 ChromaDB Search Results: Retrieved {len(chunks)} chunks (Best Proximity Dist: {best_dist:.4f} -> Grounding: {grounding_status})")
    
    # 2. Execute dynamic web fallback based on vector certainty parameters
    web_sources = []
    triggered_web_search = False
    
    if not has_grounding or state.pipeline_context.get("force_deep_research", False):
        triggered_web_search = True
        logger.info("   🌐 Grounding below threshold or Deep Research active! Launching live Trafilatura web-scraping cluster...")
        web_sources = await search_live_web(queries)
        logger.info(f"   └── 📥 Web Search Results: Extracted {len(web_sources)} live web documents.")
    else:
        logger.info("   ⏭️ Vector context grounding secure. Skipping live web-scraping pass.")

    # 3. Print a clean summary matrix to your shell console
    logger.info("   📊 FINAL DATA MATRIX RETRIEVAL SUMMARY:")
    logger.info(f"      ├── ChromaDB Chunks Loaded : {len(chunks)}")
    logger.info(f"      └── Web Scraper Loaded     : {len(web_sources)} (Triggered: {triggered_web_search})")

    # Process strings into an unified reference body
    context_lines = [f"[LOCAL MATERIAL]\n{c.get('document', '')}" for c in chunks] + \
                    [f"[WEB SOURCE: {s['title']} | URL: {s['url']}]\n{s['content']}" for s in web_sources]
    formatted_string = "\n\n---\n\n".join(context_lines)

    ms = int((time.perf_counter() - start_time) * 1000)
    
    return {
        "pipeline_context": {
            "retrieved_chunks": chunks,
            "online_sources": web_sources,
            "formatted_context_string": formatted_string
        },
        "performance_metrics_ms": {
            "research_gather_ms": ms,
            "total_sources_found": len(chunks) + len(web_sources)
        },
        "messages": [
            AIMessage(
                content="", 
                additional_kwargs={
                    "status": "🔍", 
                    "telemetry": f"Grounding {grounding_status}. Retrieved {len(chunks)} chunks and {len(web_sources)} web documents."
                }
            )
        ]
    }


async def synthesize_research_node(state: GlobalState) -> Dict[str, Any]:
    """Node: Synthesizes gathered dataset into a citation-tracked technical reply."""
    start_time = time.perf_counter()
    
    model = get_model_by_tier(state.allocated_model_tier)
    context_data = state.pipeline_context.get("formatted_context_string", "No reference data loaded.")
    
    logger.info("🧠 [RESEARCH SUBGRAPH] Dispatching dataset to Synthesis Generation Node...")
    
    try:
        response = await (PROMPT_SYNTHESIS | model).ainvoke({
            "context_string": context_data,
            "query": state.forward_query
        })
        reply = response.content
    except Exception as e:
        reply = f"❌ Technical synthesis processing sequence failed: {str(e)}"
        response = AIMessage(content=reply)

    ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"✅ [RESEARCH SUBGRAPH] Synthesis generation complete in {ms}ms.")

    return {
        "final_assistant_reply": reply,
        "performance_metrics_ms": {"research_synthesis_ms": ms},
        "messages": [response]
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

compiled_research_graph = builder.compile()