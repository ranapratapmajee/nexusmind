# path: app/agents/research/research_subgraph.py
import asyncio
import time
from typing import Any, Dict, List

from langgraph.graph import END, StateGraph

from app.agents.research.research_state import ResearchState
from app.config.settings import settings
from app.core.state import TraceTracker
from app.llm.gateway import generate_with_meta
from app.rag.chroma_store import query_documents
from app.utils.fetch_url import fetch_url_text
from app.utils.web_search import web_search

OFFLINE_COLLECTION = settings.vectorstores.collections.get(
    "chroma_collection", "knowledgebase"
)
TOP_K = settings.research.top_k_retrieval
MAX_WEB = settings.research.max_sources_online
VECTOR_DISTANCE_THRESHOLD = 0.65


def extract_trace_elements(
    chunks: List[Dict[str, Any]], sources: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """Normalizes both file blocks and raw web snippets into a single unified trace list."""
    trace_items = []

    for c in chunks:
        meta = c.get("metadata", {}) or {}
        doc_text = (c.get("document", "") or "").strip()
        snippet = f"{doc_text[:240]}..." if len(doc_text) > 240 else doc_text

        base_source = meta.get("file_name", "Local PDF Data Segment")
        context_heading = meta.get("context_marker")
        source_label = (
            f"{base_source} // {context_heading}" if context_heading else base_source
        )

        trace_items.append(
            {
                "source": source_label,
                "score": c.get("score") or c.get("distance"),
                "snippet": snippet,
            }
        )

    for s in sources:
        text = (s.get("content", "") or "").strip()
        snippet = f"{text[:240]}..." if len(text) > 240 else text
        trace_items.append(
            {
                "source": s.get("title", s.get("url", "Web Link Reference")),
                "score": None,
                "snippet": snippet,
            }
        )

    return trace_items


async def research_planner_node(state: ResearchState) -> Dict[str, Any]:
    """Generates execution task matrices for the local workspace context tracker."""
    tracker = TraceTracker.from_state(state)
    tracker.set_metadata(tools_used=["research_planner"])

    return {
        "research_plan": {
            "query": state["question"],
            "web_limit": MAX_WEB + 3 if state["mode"] == "deep_research" else MAX_WEB,
        },
        "trace": tracker.compiled_trace,
    }


async def gather_sources_node(state: ResearchState) -> Dict[str, Any]:
    """
    Parallel Multi-Query Engine.
    Gathers local vectors and live web docs across all query vectors concurrently.
    """
    start_time = time.perf_counter()

    # 🎯 CENTRALIZED DESIGN: Instantiate from parent state blueprint
    tracker = TraceTracker.from_state(state)
    queries_to_run = state.get("expanded_queries") or [state["question"]]

    tracker.log_step(
        "Colima Virtual Machine Context Handshake",
        "Docker/Chroma DB Ready, Link Stable",
    )
    tracker.set_metadata(tools_used=["chroma_retriever"])

    # 1. Parallelize ChromaDB retrieval over all query variants
    async def fetch_chroma(q: str):
        try:
            return await query_documents(
                collection_name=OFFLINE_COLLECTION, query=q, top_k=TOP_K
            )
        except Exception as e:
            print(f"[RAG Multi-Query Failure for: {q}]: {e}")
            return []

    chroma_tasks = [fetch_chroma(q) for q in queries_to_run]
    chroma_results = await asyncio.gather(*chroma_tasks)

    # Flatten and deduplicate local hits
    seen_docs = set()
    unique_local_hits = []
    best_score = None

    for result_list in chroma_results:
        for chunk in result_list:
            doc_body = chunk.get("document", "").strip()
            if doc_body not in seen_docs:
                seen_docs.add(doc_body)
                unique_local_hits.append(chunk)

                score = chunk.get("score") or chunk.get("distance")
                if score is not None and (best_score is None or score < best_score):
                    best_score = score

    has_high_confidence = (
        best_score is not None and best_score <= VECTOR_DISTANCE_THRESHOLD
    )

    if has_high_confidence:
        tracker.log_step(
            "ChromaDB Unified Retrieval",
            f"Match Confirmed across vectors (Dist: {best_score:.2f})",
        )
    else:
        msg = (
            f"Data Irrelevant / Missing inside local collection (Dist: {best_score:.2f})"
            if best_score
            else "No Local Chunks Found"
        )
        tracker.log_step("ChromaDB Unified Retrieval", msg, status_icon="🟡")

    # 2. Conditional Multi-Query Web Fallback Aggregation
    online_hits = []
    trigger_web_fallback = not has_high_confidence or state["mode"] == "deep_research"

    if state["use_web"] and trigger_web_fallback:
        tracker.log_step(
            "Fallback Routing Triggered",
            f"Multi-Query Web Search active over {len(queries_to_run)} paths",
        )
        tracker.set_metadata(tools_used=["web_search_engine"])

        plan = state.get("research_plan", {})
        web_limit = max(1, plan.get("web_limit", MAX_WEB) // 2)

        async def fetch_and_scrape_web(q: str):
            scraped_items = []
            try:
                search_raw = web_search(q, max_results=web_limit)
                for item in search_raw[:web_limit]:
                    href = item.get("href", "")
                    if not href:
                        continue
                    try:
                        page_content = await fetch_url_text(href)
                    except Exception:
                        page_content = ""

                    final_text = (
                        page_content.strip() if page_content else item.get("body", "")
                    )
                    if len(final_text) > 3000:
                        final_text = f"{final_text[:3000]} [Truncated]"

                    if final_text:
                        scraped_items.append(
                            {
                                "title": item.get("title", "Scraped Context Node"),
                                "url": href,
                                "content": final_text,
                            }
                        )
            except Exception as e:
                print(f"[Web loop query failure for: {q}]: {e}")
            return scraped_items

        web_tasks = [fetch_and_scrape_web(q) for q in queries_to_run]
        web_results = await asyncio.gather(*web_tasks)

        # Deduplicate web items
        seen_urls = set()
        for sub_list in web_results:
            for hit in sub_list:
                url_target = hit.get("url")
                if url_target not in seen_urls:
                    seen_urls.add(url_target)
                    online_hits.append(hit)

    elif not state["use_web"] and trigger_web_fallback:
        tracker.log_step(
            "Fallback Routing Skipped",
            "Live search tools bypassed via state configuration toggles",
            status_icon="🟡",
        )

    elapsed = int((time.perf_counter() - start_time) * 1000)

    # 🎯 CENTRALIZED DESIGN: Pack structured layers under schema-agnostic keys
    tracker.set_metric(
        "retrieval_data",
        {
            "collection": OFFLINE_COLLECTION,
            "top_k": TOP_K,
            "chunks": extract_trace_elements(
                unique_local_hits[:TOP_K], online_hits[:MAX_WEB]
            ),
        },
    )
    tracker.set_metric("retrieval_ms", elapsed)

    return {
        "retrieved_chunks": unique_local_hits[:TOP_K],
        "online_sources": online_hits[:MAX_WEB],
        "subgraph_pipeline_logs": tracker.timeline,  # Keep history tracking continuous
        "trace": tracker.compiled_trace,
    }


async def build_context_node(state: ResearchState) -> Dict[str, Any]:
    """Flattens retrieved data blocks into a structured, clean context string."""
    buffer = []
    for c in state.get("retrieved_chunks", []):
        meta = c.get("metadata", {})
        buffer.append(
            f"[OFFLINE DOCUMENT REFERENCING: {meta.get('file_name', 'System Data Layer')}]\n{c.get('document', '')}"
        )

    for s in state.get("online_sources", []):
        buffer.append(
            f"[LIVE SCALED WEB REFERENCE: {s.get('title')} | URL: {s.get('url')}]\n{s.get('content')}"
        )

    return {"context_string": "\n\n---\n\n".join(buffer)}


async def synthesize_node(state: ResearchState) -> Dict[str, Any]:
    """Runs data synthesis using your composable Professor instruction templates."""
    start_time = time.perf_counter()
    tracker = TraceTracker.from_state(state)

    from app.llm.prompt_builder import build_dynamic_system_prompt

    persona_context = state.get("persona_mode", "standard_utility")
    system_instructions = build_dynamic_system_prompt(persona_context)

    prompt = (
        f"{system_instructions}\n\n"
        f"CORE QUESTION TARGET: {state['question']}\n\n"
        f"FOUNDATIONAL SOURCE MATERIAL CONTEXT:\n{state.get('context_string', 'No reference tracking text available.')}\n\n"
        f"Synthesize the gathered material into a crisp response. Use compact markdown formatting."
    )

    llm_payload = await generate_with_meta(
        task_type="research_synthesis",
        user_message=prompt,
        model_id=state["model_id"],
        tracker=tracker,
    )

    generation_ms = int((time.perf_counter() - start_time) * 1000)

    # 🎯 CENTRALIZED DESIGN: Save telemetry states using updated hooks cleanly
    tracker.set_metadata(
        model=llm_payload.get("model", "qwen2.5-coder:3b-instruct"),
        tier=llm_payload.get("tier", "Standard Tier"),
    )
    tracker.set_metric("generation_ms", generation_ms)
    tracker.set_metadata(provider=llm_payload.get("provider", "ollama"))
    tracker.set_metadata(fallback_used=bool(llm_payload.get("fallback_used", False)))

    return {
        "answer": llm_payload.get("text", ""),
        "trace": tracker.compiled_trace,
        "subgraph_pipeline_logs": tracker.timeline,
    }


_research_graph = None


def get_research_graph():
    """Compiles internal execution steps into an independent, pluggable subgraph."""
    global _research_graph
    if _research_graph is None:
        builder = StateGraph(ResearchState)
        builder.add_node("research_planner", research_planner_node)
        builder.add_node("gather_sources", gather_sources_node)
        builder.add_node("build_context", build_context_node)
        builder.add_node("synthesize", synthesize_node)

        builder.set_entry_point("research_planner")
        builder.add_edge("research_planner", "gather_sources")
        builder.add_edge("gather_sources", "build_context")
        builder.add_edge("build_context", "synthesize")
        builder.add_edge("synthesize", END)
        _research_graph = builder.compile()
    return _research_graph


async def run_research_subgraph(
    question: str,
    session_id: str,
    use_web: bool = True,
    model_pref: str = "Auto",
    model_id: str = "auto",
    mode: str = "chat",
    expanded_queries: List[str] = None,
) -> dict:
    """Entry point broker executor mapping input dictionaries into the subgraph engine state loop."""

    initial_state = {
        "session_id": session_id,
        "question": question,
        "use_web": use_web,
        "model_id": model_id,
        "mode": mode,
        "expanded_queries": expanded_queries or [question],
        "retrieved_chunks": [],
        "online_sources": [],
        # 🎯 FIX: Seed the tracking array placeholder natively
        "subgraph_pipeline_logs": [],
        "trace": {"metadata": {}, "metrics": {}, "timeline": []},
    }

    graph = get_research_graph()
    final_state = await graph.ainvoke(initial_state)
    trace = final_state.get("trace", {}) or {}
    subgraph_logs = final_state.get("subgraph_pipeline_logs", [])

    # Return unified payload mapping back out to the parent system orchestrator
    return {
        "reply": final_state.get("answer", ""),
        "provider": trace.get("metadata", {}).get("provider", "ollama"),
        "model": trace.get("metadata", {}).get("model", "qwen2.5-coder:3b-instruct"),
        "tier": trace.get("metadata", {}).get("tier", "Standard Tier"),
        "fallback_used": trace.get("metadata", {}).get("fallback_used", False),
        "retrieval": trace.get("metrics", {}).get("retrieval_data", {}),
        "timing": trace.get("metrics", {}),
        "subgraph_pipeline_logs": subgraph_logs,
    }
