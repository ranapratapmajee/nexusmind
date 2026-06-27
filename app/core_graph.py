# path: app/core_graph.py

import re
import time
import logging
from typing import Any, Dict, List, Tuple
from langgraph.graph import START, END, StateGraph

from app.settings import settings
from app.llm_gateway import generate_with_meta
from app.state_models import GlobalState, PipelineTraceLog
from app.graphs.research_graph import compiled_research_graph

logger = logging.getLogger("nexusmind.core_graph")

# =========================================================================
# 🛡️ 1. GOVERNANCE & COMPLIANCE INTERCEPTORS
# =========================================================================

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?prior\s+instructions", re.IGNORECASE),
    re.compile(r"reveal\s+(?:your\s+)?system\s+(?:prompt|instructions)", re.IGNORECASE),
    re.compile(r"system\s*prompt\s*disclosure", re.IGNORECASE)
]

PII_PATTERNS = {
    "SOCIAL_SECURITY_NUMBER": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "IPv4_ADDRESS": re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"),
    "CREDIT_CARD_NUMBER": re.compile(r"\b(?:\d{4}[-\s]?){3}\d{4}\b")
}

VALID_DOMAINS = ["code", "algorithm", "learn", "study", "explain", "architecture", "ai", "ml", "rag", "search"]

def run_input_guardrails(query: str) -> Tuple[bool, str, str]:
    txt = query.strip()
    if not txt:
        return False, "", "❌ Empty stream buffer string submitted."

    if any(p.search(txt) for p in INJECTION_PATTERNS):
        return False, txt, "🚨 **Security Protocol Alert:** Malicious override sequence detected."

    for label, regex in PII_PATTERNS.items():
        if regex.search(txt):
            txt = regex.sub(f"[{label}_REDACTED]", txt)

    lower_txt = txt.lower()
    is_casual = any(g in lower_txt for g in ["hi", "hello", "hey", "clear", "test"])
    has_domain = any(d in lower_txt for d in VALID_DOMAINS)
    
    if not (is_casual or has_domain):
        return False, txt, "⚠️ **Domain Alignment Flag:** Focus limits are set to technical study and AI/ML engineering."

    return True, txt, ""

def create_trace(state: GlobalState, node_name: str, message: str, status: str = "🟢") -> List[PipelineTraceLog]:
    return [PipelineTraceLog(
        step_number=len(state.chronological_trace_logs) + 1,
        execution_status=status,
        node_identifier=node_name,
        telemetry_message=message
    )]

# =========================================================================
# 🎛️ 2. CORE GRAPH NODES (NATIVE STATE MERGING)
# =========================================================================

async def governance_node(state: GlobalState) -> Dict[str, Any]:
    start = time.perf_counter()
    passed, sanitized, error_msg = run_input_guardrails(state.raw_user_query)
    ms = int((time.perf_counter() - start) * 1000)
    
    updated_metrics = {**state.performance_metrics_ms, "governance_ms": ms}

    if not passed:
        return {
            "final_assistant_reply": error_msg,
            "routing_compute_tier": "TERMINATED",
            "chronological_trace_logs": create_trace(state, "Security Check Engine", "Security guardrails breached. Intercepted.", "🔴"),
            "performance_metrics_ms": updated_metrics
        }

    return {
        "sanitized_user_query": sanitized,
        "chronological_trace_logs": create_trace(state, "Security Check Engine", "Input governance verification clear."),
        "performance_metrics_ms": updated_metrics
    }


async def router_node(state: GlobalState) -> Dict[str, Any]:
    """🧠 Evaluates complexity and establishes the path assignment."""
    start = time.perf_counter()
    
    if state.ui_requested_mode == "deep_research":
        classification = "HIGH"
    else:
        prompt = (
            "You are an expert system orchestrator intent routing classifier.\n"
            "Analyze the user's query carefully and respond with exactly one word: 'HIGH' or 'LOW'.\n\n"
            f"Query to evaluate: {state.sanitized_user_query}\n"
            "Classification Output:"
        )
        try:
            res = await generate_with_meta(task_type="intent_routing", user_message=prompt, model_id=settings.OLLAMA_MODEL)
            classification = res.get("text", "LOW").strip().upper()
            classification = "HIGH" if "HIGH" in classification else "LOW"
        except Exception:
            classification = "LOW"

    is_high = classification == "HIGH"
    target = "research" if is_high else "direct_llm"
    model = settings.GEMINI_MODEL if is_high else settings.OLLAMA_MODEL
    
    updated_metrics = {**state.performance_metrics_ms, "router_ms": int((time.perf_counter() - start) * 1000)}
    
    return {
        "target_pipeline_key": target,
        "routing_compute_tier": "HIGH" if is_high else "LOW",
        "dynamic_persona_mode": "socratic_professor" if is_high else "standard_utility",
        "allocated_model_id": model,
        "chronological_trace_logs": create_trace(state, f"Intent Router ({classification})", f"Allocated Target Pipeline Matrix: [{target.upper()}]"),
        "performance_metrics_ms": updated_metrics
    }


async def fast_conversational_node(state: GlobalState) -> Dict[str, Any]:
    """Handles direct utility chats on local fast silicon."""
    start = time.perf_counter()
    res = await generate_with_meta(
        task_type="generic_chat", 
        user_message=state.sanitized_user_query, 
        model_id=state.allocated_model_id
    )
    
    updated_metrics = {**state.performance_metrics_ms, "direct_llm_ms": int((time.perf_counter() - start) * 1000)}

    return {
        "final_assistant_reply": res.get("text", "").strip(),
        "chronological_trace_logs": create_trace(state, "Fast Chat Engine", "Processing instantly via local hardware resources."),
        "performance_metrics_ms": updated_metrics
    }


async def response_node(state: GlobalState) -> Dict[str, Any]:
    """Aggregates metrics and drops a clean terminal handshake log."""
    updated_metrics = dict(state.performance_metrics_ms)
    total_ms = sum(v for v in updated_metrics.values() if isinstance(v, (int, float)))
    updated_metrics["total_ms"] = total_ms
    
    return {
        "chronological_trace_logs": create_trace(state, "Terminal Response Handshake", f"Execution lifecycle completed in {total_ms}ms", "🏁"),
        "performance_metrics_ms": updated_metrics
    }

# =========================================================================
# 🏗️ 3. WORKFLOW TOPOLOGY COMPILER (NATIVE SUBGRAPH ADDITION)
# =========================================================================

def get_master_graph():
    builder = StateGraph(GlobalState)
    
    builder.add_node("governance", governance_node)
    builder.add_node("router", router_node)
    builder.add_node("fast_conversational", fast_conversational_node)
    
    # 🟢 NATIVE SUBGRAPH ATTACHMENT: No proxies or registries required.
    # LangGraph completely natively manages state flow and sub-computes here.
    builder.add_node("execute_research_subgraph", compiled_research_graph)
    
    builder.add_node("response", response_node)
    
    builder.add_edge(START, "governance")
    
    builder.add_conditional_edges(
        "governance",
        lambda state: "halt" if state.routing_compute_tier == "TERMINATED" else "continue",
        {"halt": "response", "continue": "router"}
    )
    
    builder.add_conditional_edges(
        "router",
        lambda state: state.target_pipeline_key,
        {
            "direct_llm": "fast_conversational",
            "research": "execute_research_subgraph"
        }
    )
    
    builder.add_edge("fast_conversational", "response")
    builder.add_edge("execute_research_subgraph", "response")
    builder.add_edge("response", END)
    
    return builder.compile()