# path: frontend/ui/chat_ui.py
import streamlit as st
from ui.trace_ui import render_trace


def render_chat_header() -> None:
    """Renders a centered, clean developer landing hero workspace view."""
    st.markdown(
        """
        <div class="nexa-hero" style="text-align: center; margin-top: 8vh; margin-bottom: 4vh;">
            <div class="nexa-eyebrow" style="font-family: monospace; font-size: 0.85rem; color: #6366F1; font-weight: 600; letter-spacing: 1px; margin-bottom: 4px;">NEXUS // CORE</div>
            <div class="nexa-title" style="font-size: 1.75rem; font-weight: 700; letter-spacing: -0.5px;">Ask anything. Research deeply.</div>
            <div class="nexa-subtitle" style="font-size: 0.85rem; opacity: 0.6; max-width: 520px; margin: 8px auto 0 auto; line-height: 1.4;">
                A high-density engineering workspace for AI/ML study, source-grounded exploration,
                and autonomous execution tracing.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_messages() -> None:
    """Safely iterates history lists and manages landing layout conditions."""
    messages = st.session_state.get("messages", [])

    user_has_messaged = any(msg.get("role") == "user" for msg in messages)
    if not user_has_messaged:
        render_chat_header()

    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")

        # Pull raw trace dictionary stream
        trace = msg.get("trace", {}) or {}

        # 1. Render primary chat element natively
        with st.chat_message(role):
            st.markdown(content)

        # 2. Render trace block aligned with the chat bubble box bounds
        if role == "assistant" and trace:
            # Create an explicit asymmetric layout grid column array.
            trace_col, spacer_col = st.columns([0.84, 0.16])

            with trace_col:
                st.markdown(
                    "<div style='margin-top: -12px; margin-bottom: 16px;'></div>",
                    unsafe_allow_html=True,
                )

                # 🎯 CLEAN CENTRALIZED HANDSHAKE:
                # Read the array directly out of the unified telemetry payload.
                # If the backend omitted it or it's empty, fall back safely.
                pipeline_history = trace.get("pipeline_trace_history", [])

                # Render the clean execution tree panel
                render_trace(trace=trace, pipeline_trace_history=pipeline_history)
