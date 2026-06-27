# path: frontend/ui/composer_ui.py

from typing import Any, Dict
import requests
import streamlit as st
from ui.api_client import call_backend
from ui.formatters import get_enabled_models, get_model_label_map


def render_composer() -> None:
    """Renders a simplified floating control bar and native chat input element."""
    modes = st.session_state.get("available_modes", ["chat", "deep_research"])
    enabled_models = get_enabled_models(st.session_state.model_catalog)
    model_label_map = get_model_label_map(enabled_models)
    model_ids = list(model_label_map.keys())

    if st.session_state.selected_model_id not in model_ids and model_ids:
        st.session_state.selected_model_id = model_ids[0]

    footer_container = st.bottom
    with footer_container:
        st.markdown("<div style='margin-bottom: -10px;'></div>", unsafe_allow_html=True)

        col_mode, col_model = st.columns([4, 2], vertical_alignment="center")
        with col_mode:
            selected_mode = st.pills(
                "Mode Selector",
                options=modes,
                default=st.session_state.selected_mode if st.session_state.selected_mode in modes else "chat",
                format_func=lambda x: "✨ Nexa Chat" if x == "chat" else "🔬 Deep Research",
                selection_mode="single",
                label_visibility="collapsed",
                key="pills_mode_selector",
            )
            if selected_mode:
                st.session_state.selected_mode = selected_mode

        with col_model:
            selected_model = st.selectbox(
                "Model Selector",
                options=model_ids,
                format_func=lambda x: model_label_map.get(x, x),
                key="composer_model",
                label_visibility="collapsed",
            )
            st.session_state.selected_model_id = selected_model

        user_input = st.chat_input(
            placeholder="Ask Nexa anything...",
            disabled=st.session_state.is_waiting_for_response,
            key="nexa_chat_input",
        )

    if user_input and not st.session_state.is_waiting_for_response:
        clean_input = user_input.strip()
        if clean_input:
            st.session_state.messages.append({"role": "user", "content": clean_input})
            st.session_state.pending_request = {
                "message": clean_input,
                "session_id": st.session_state.session_id,
                "backend_url": st.session_state.backend_url,
                "model_id": st.session_state.selected_model_id,
                "mode": st.session_state.selected_mode,
            }
            st.session_state.is_waiting_for_response = True
            st.rerun()


def process_pending_request() -> None:
    """Orchestrates network payload transmissions and updates local historical state keys."""
    pending = st.session_state.pending_request
    if not pending:
        return

    reply = ""
    trace_logs = []
    metrics = {}

    with st.spinner("Nexa is analyzing request pipeline..."):
        try:
            result = call_backend(
                message=pending["message"],
                session_id=pending["session_id"],
                backend_url=pending["backend_url"],
                model_id=pending["model_id"],
                mode=pending["mode"],
            )
            reply = result.get("reply", "")
            trace_logs = result.get("trace_logs", [])
            metrics = result.get("metrics", {})

        except requests.exceptions.RequestException as e:
            reply = f"I couldn't reach the backend server pipeline endpoint. Ensure your server is live.\n\nError: `{e}`"
            trace_logs = [
                {"step_number": 1, "execution_status": "🟢", "node_identifier": "User Request Entry", "telemetry_message": "Payload Ingested"},
                {"step_number": 2, "execution_status": "🔴", "node_identifier": "FastAPI Network Bridge", "telemetry_message": "Connection Timed Out: Endpoint Unreachable"}
            ]
        except Exception as e:
            reply = f"System Processing Failure: `{e}`"
            trace_logs = [
                {"step_number": 1, "execution_status": "🟢", "node_identifier": "User Request Entry", "telemetry_message": "Payload Ingested"},
                {"step_number": 2, "execution_status": "🔴", "node_identifier": "Runtime Error Intercept", "telemetry_message": f"Exception raised: {str(e)[:40]}"}
            ]

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": reply,
            "trace_logs": trace_logs,
            "metrics": metrics,
        }
    )
    st.session_state.pending_request = None
    st.session_state.is_waiting_for_response = False
    st.rerun()