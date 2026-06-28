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

async def gather_sources_node(state: GlobalState) -> Dict[str, Any]:
    """Node: Aggregates local vector chunks and live web lookups dynamically."""
    start_time = time.perf_counter()
    
    # Safely look for search term queries using your renamed forward_query fallback variable
    queries = state.pipeline_context.get("expanded_queries") or [state.forward_query]
    
    logger.info("📡 [RESEARCH SUBGRAPH] Initializing Parallel Retrieval Matrix... 🔍 Processing Query Variations: {queries}")
    
    # 1. Execute local vector lookup
    logger.info("   🗄️ Invoking ChromaDB Vector Store client...")
    chunks, best_dist, has_grounding = await search_local_vectorbase(queries)
    grounding_status = "confirmed" if has_grounding else "below threshold"
    
    logger.info(f"📥 [RESEARCH SUBGRAPH] ChromaDB Search Results: Retrieved {len(chunks)} chunks (Best Proximity Dist: {best_dist:.4f} -> Grounding: {grounding_status})")
    
    # 2. Execute dynamic web fallback based on vector certainty parameters
    web_sources = []
    triggered_web_search = False
    
    if not has_grounding or state.pipeline_context.get("force_deep_research", False):
        triggered_web_search = True
        logger.info("   🌐 Grounding below threshold or Deep Research active! Launching web search ...")
        web_sources = await search_live_web(queries)
        logger.info(f"📥 [RESEARCH SUBGRAPH] Web Search Results: Extracted {len(web_sources)} live web documents.")
    else:
        logger.info("   ⏭️ Vector context grounding secure. Skipping web search tool.")

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
    """Node: Synthesizes gathered dataset into a citation-tracked technical reply via native streaming."""
    start_time = time.perf_counter()
    
    model = get_model_by_tier(state.allocated_model_tier)
    context_data = state.pipeline_context.get("formatted_context_string", "No reference data loaded.")
    
    logger.info("🧠 [RESEARCH SUBGRAPH] Dispatching dataset to Synthesis Generation Node...")
    
    full_content = ""
    try:
        # Loop over the stream chunks so LangGraph's event manager can broadcast them live
        async for chunk in (PROMPT_SYNTHESIS | model).astream({
            "context_string": context_data,
            "query": state.forward_query
        }):
            if chunk.content:
                full_content += chunk.content
    except Exception as e:
        logger.error(f"❌ Synthesis token generation failed: {e}")
        full_content = f"❌ Technical synthesis processing sequence failed: {str(e)}"

    ms = int((time.perf_counter() - start_time) * 1000)
    logger.info(f"✅ [RESEARCH SUBGRAPH] Synthesis generation complete in {ms}ms.")

    return {
        "final_assistant_reply": full_content,
        "performance_metrics_ms": {"research_synthesis_ms": ms},
        "messages": [AIMessage(content=full_content)]
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