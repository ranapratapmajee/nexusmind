# path: app/core/graph.py
import time
from typing import Any, Dict

from langgraph.graph import END, StateGraph

from app.agents.research.research_subgraph import run_research_subgraph
from app.config.settings import settings
from app.core.guardrails import NexusGuardrails
from app.core.state import NexusState, TraceTracker
from app.llm.gateway import generate_with_meta

# Initialize local safety and compliance controller
guardrails = NexusGuardrails()


async def governance_node(state: NexusState) -> Dict[str, Any]:
    """
    Tier 1 & 2 Governance & Redaction Edge Node.
    Initializes tracking matrices and hooks into guardrail telemetry streams.
    """
    node_start = time.perf_counter()
    node_name = "governance_node"

    user_msg = state.get("user_message") or state.get("message") or ""

    # Unpack the telemetry logs constructed dynamically inside guardrails V2 check
    passed, flags, sanitized_msg, initial_logs = guardrails.verify_input_safety(
        str(user_msg), existing_trace=state.get("trace", {})
    )
    elapsed_ms = int((time.perf_counter() - node_start) * 1000)

    # 🎯 CENTRALIZED DESIGN: Instantiate from parent state or start clean
    tracker = TraceTracker(trace_state=state.get("trace", {}))
    tracker.set_metadata(
        route="SECURITY_CHECK",
        mode="edge_validation",
        model="NEXUS_GUARD_V2",
        tier="LOCAL_EDGE",
        tools_used=["regex_guardrails", "token_masker"],
    )
    tracker.set_metric(f"{node_name}_ms", elapsed_ms)

    # Stitch the safety validation logs directly into the history timeline
    tracker.log_external_sequence(initial_logs or [])

    if not passed:
        refusal_reply = guardrails.intercept_and_generate_rejection(flags)
        tracker.log_step(
            node_name,
            "Security guardrails breached. Request intercepted.",
            status_icon="🔴",
        )

        return {
            "governance_passed": False,
            "security_flags": flags,
            "assistant_reply": refusal_reply.strip(),
            "next_step": "finalizer",
            "trace": tracker.compiled_trace,
            "pipeline_trace_history": tracker.timeline,
        }

    tracker.log_step(node_name, "Input governance verification clear.")

    return {
        "governance_passed": True,
        "user_message": sanitized_msg,
        "next_step": "planner",
        "security_flags": flags if flags else ["NONE"],
        "trace": tracker.compiled_trace,
        "pipeline_trace_history": tracker.timeline,
    }


async def planner_node(state: NexusState) -> Dict[str, Any]:
    """
    Enterprise Semantic Complexity Classifier Router.
    Uses heuristic fast-paths for simple queries to save compute,
    and reserves LLM classification for complex architectural analysis.
    """
    node_start = time.perf_counter()
    node_name = "planner_node"

    tracker = TraceTracker.from_state(state)
    query = str(state.get("user_message") or state.get("message") or "").strip()
    requested_mode = state.get("ui_requested_mode", "chat")

    is_complex = False
    classification = "LOW"
    fast_path_triggered = False

    # ⚡ HEURISTIC FAST-PATH: Bypass LLM classification for simple queries
    if requested_mode != "deep_research":
        lower_query = query.lower()
        short_greetings = ["hi", "hello", "hey", "test", "ping", "sup", "clear"]

        # If it's a known greeting, or extremely short (< 4 words) without technical jargon
        is_short = len(query.split()) < 4
        has_jargon = any(
            word in lower_query
            for word in ["how", "why", "code", "error", "bug", "build", "create", "fix"]
        )

        if lower_query in short_greetings or (is_short and not has_jargon):
            fast_path_triggered = True
            classification = "LOW"
            tracker.log_step(
                "Intent Routing", "Heuristic fast-path engaged. LLM bypass successful."
            )

    # 🧠 LLM CLASSIFICATION: Only run if the fast-path didn't catch it
    if not fast_path_triggered:
        routing_prompt = (
            "Task: Classify if the user query is a highly complex technical, "
            "architectural, or source-grounded code/math question requiring deep analysis "
            "or external reference information.\n"
            f'Query: "{query}"\n\n'
            "Respond with exactly one word: 'HIGH' for deep engineering/architecture tasks, "
            "or 'LOW' for casual greeting/basic text help. Do not include extra text."
        )

        try:
            classification_res = await generate_with_meta(
                task_type="intent_routing",
                user_message=routing_prompt,
                model_id="auto",
                tracker=tracker,
            )
            classification = classification_res.get("text", "LOW").strip().upper()
        except Exception:
            classification = "LOW"

    # Route Decider Logic
    is_complex = "HIGH" in classification or "DEEP" in classification
    final_route = (
        "deep_research" if (requested_mode == "deep_research" or is_complex) else "chat"
    )

    mode_label = (
        "⚡ Dynamic Route"
        if is_complex
        else ("🟢 Heuristic Route" if fast_path_triggered else "🟢 Auto-Routed")
    )
    persona_label = (
        "🔷 Deep Analysis"
        if final_route == "deep_research"
        else "🤖 Standard Assistant"
    )

    model_id = state.get("selected_model_id", "auto")
    if final_route == "deep_research" and (model_id == "auto" or "qwen" in model_id):
        gemini_provider = settings.llm.providers.get("gemini")
        model_id = gemini_provider.model if gemini_provider else "gemini-2.5-flash"
    elif model_id == "auto":
        model_id = "qwen2.5-coder:3b-instruct"

    elapsed_ms = int((time.perf_counter() - node_start) * 1000)

    tracker.set_metadata(
        route=final_route.upper(),
        mode=f"{persona_label} | {mode_label}",
        model=model_id,
        tier="Advanced Reasoning"
        if final_route == "deep_research"
        else "Standard Stream",
        tools_used=["semantic_intent_classifier"]
        if not fast_path_triggered
        else ["heuristic_router"],
    )
    tracker.set_metric(f"{node_name}_ms", elapsed_ms)

    tracker.log_step(
        activity_name=f"Intent Classifier ({mode_label})",
        status_msg=f"Allocated Tier: {persona_label}",
    )

    return {
        "current_intent_route": final_route,
        "persona_mode": "socratic_professor"
        if final_route == "deep_research"
        else "standard_utility",
        "selected_model_id": model_id,
        "next_step": "query_expansion"
        if final_route == "deep_research"
        else "direct_llm",
        "trace": tracker.compiled_trace,
        "pipeline_trace_history": tracker.timeline,
    }


async def query_expansion_node(state: NexusState) -> Dict[str, Any]:
    """
    Step 1.1: Multi-Query Generation Node.
    Expands the baseline question into three variations to optimize cross-tier retrieval.
    """
    node_start = time.perf_counter()
    node_name = "query_expansion_node"

    tracker = TraceTracker.from_state(state)
    query = str(state.get("user_message") or state.get("message") or "").strip()

    expansion_prompt = (
        "Task: Generate exactly three distinct search query variations optimized for "
        "code/documentation vector search matching the core technical problem.\n"
        f"Original Query: {query}\n\n"
        "Output Requirements:\n"
        "- Provide exactly 3 queries, one per line.\n"
        "- Do not use bullet points, numbering, or wrapping quotes.\n"
        "- Do not include introductory or explanatory conversational text."
    )

    try:
        res = await generate_with_meta(
            task_type="query_expansion",
            user_message=expansion_prompt,
            model_id="qwen2.5-coder:3b-instruct",
            tracker=tracker,
        )
        raw_text = res.get("text", "").strip()
        expanded_queries = [
            line.strip() for line in raw_text.split("\n") if line.strip()
        ][:3]
    except Exception:
        expanded_queries = []

    if len(expanded_queries) < 3:
        expanded_queries = [query, f"{query} documentation", f"{query} implementation"]

    elapsed_ms = int((time.perf_counter() - node_start) * 1000)

    tracker.set_metadata(tools_used=["query_expansion_engine"])
    tracker.set_metric(f"{node_name}_ms", elapsed_ms)

    tracker.log_step(
        activity_name="Query Expansion Engine",
        status_msg=f"Generated {len(expanded_queries)} search vectors for RAG optimization",
    )

    return {
        "expanded_queries": expanded_queries,
        "trace": tracker.compiled_trace,
        "pipeline_trace_history": tracker.timeline,
    }


def route_decDecider(state: NexusState) -> str:
    """
    Evaluates next step tracking variables to route conditional graph edges.
    Enforces safe structural checks to block execution thread freezes.
    """
    target = state.get("next_step")
    valid_nodes = [
        "planner",
        "query_expansion",
        "direct_llm",
        "research_agent",
        "finalizer",
    ]

    if target in valid_nodes:
        return target

    return "finalizer"


async def research_agent_node(state: NexusState) -> Dict[str, Any]:
    """
    Step 1.2: Autonomous Multi-Source Retrieval Synthesis Node.
    Passes expanded query variants down and unifies the pipeline history metrics.
    """
    node_start = time.perf_counter()
    node_name = "research_agent_node"

    tracker = TraceTracker.from_state(state)
    user_msg = state.get("user_message") or state.get("message") or ""
    expanded_queries = state.get("expanded_queries", [user_msg])

    result = await run_research_subgraph(
        question=user_msg,
        session_id=state.get("session_id", "default"),
        use_web=True,
        model_id=state.get("selected_model_id", "auto"),
        mode=state.get("persona_mode", "standard_utility"),
        expanded_queries=expanded_queries,
    )

    # Stitch the external subgraph step log elements natively
    tracker.log_external_sequence(result.get("subgraph_pipeline_logs", []))

    elapsed_ms = int((time.perf_counter() - node_start) * 1000)

    tracker.set_metadata(
        model=result.get("model"),
        tools_used=["research_subgraph_agent"]
        + (["vector_retriever"] if result.get("retrieval") else []),
    )
    tracker.set_metric("retrieval_data", result.get("retrieval", {}))
    tracker.set_metric(f"{node_name}_ms", elapsed_ms)

    return {
        "assistant_reply": result.get("reply", "").strip(),
        "trace": tracker.compiled_trace,
        "pipeline_trace_history": tracker.timeline,
        "next_step": "finalizer",
    }


async def direct_llm_node(state: NexusState) -> Dict[str, Any]:
    """Handles standard conversational pipelines with local runtime tracking."""
    node_start = time.perf_counter()
    node_name = "direct_llm_node"

    tracker = TraceTracker.from_state(state)
    user_msg = state.get("user_message") or state.get("message") or ""

    tracker.set_metadata(tools_used=["direct_llm_chat"])
    tracker.log_step(
        activity_name="Direct Compute Execution",
        status_msg="Processing instantly via local hardware resources",
    )

    res = await generate_with_meta(
        task_type="generic_chat",
        user_message=user_msg,
        model_id=state.get("selected_model_id", "auto"),
        tracker=tracker,
    )

    elapsed_ms = int((time.perf_counter() - node_start) * 1000)
    tracker.set_metric(f"{node_name}_ms", elapsed_ms)

    return {
        "assistant_reply": res.get("text", "").strip(),
        "trace": tracker.compiled_trace,
        "pipeline_trace_history": tracker.timeline,
        "next_step": "finalizer",
    }


async def finalizer_node(state: NexusState) -> Dict[str, Any]:
    """Locks state registers and caps final performance calculations cleanly."""
    tracker = TraceTracker.from_state(state)
    metrics = tracker.compiled_trace.get("metrics", {})

    total_ms = sum(
        v for k, v in metrics.items() if k != "total_ms" and isinstance(v, (int, float))
    )

    # Clean, decentralized termination anchor assignment
    final_history = tracker.close_telemetry(total_ms)

    return {
        "next_step": "end",
        "pipeline_trace_history": final_history,
        "trace": tracker.compiled_trace,
    }


_graph = None


def get_graph():
    """Compiles the revised state infrastructure graph maps into an active execution engine."""
    global _graph
    if _graph is None:
        builder = StateGraph(NexusState)

        builder.add_node("governance", governance_node)
        builder.add_node("planner", planner_node)
        builder.add_node("query_expansion", query_expansion_node)
        builder.add_node("research_agent", research_agent_node)
        builder.add_node("direct_llm", direct_llm_node)
        builder.add_node("finalizer", finalizer_node)

        builder.set_entry_point("governance")

        builder.add_conditional_edges(
            "governance",
            route_decDecider,
            {
                "planner": "planner",
                "finalizer": "finalizer",
                "direct_llm": "direct_llm",
            },
        )

        builder.add_conditional_edges(
            "planner",
            route_decDecider,
            {
                "query_expansion": "query_expansion",
                "direct_llm": "direct_llm",
                "finalizer": "finalizer",
            },
        )

        builder.add_edge("query_expansion", "research_agent")
        builder.add_edge("research_agent", "finalizer")
        builder.add_edge("direct_llm", "finalizer")

        # 🎯 THE SOLUTION: The missing termination linkage to gracefully exit .ainvoke()
        builder.add_edge("finalizer", END)

        _graph = builder.compile()

    return _graph
