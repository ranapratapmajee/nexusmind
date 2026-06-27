# path: frontend/ui/composer_ui.py

from typing import Any, Dict
import streamlit as st
from ui.api_client import call_backend
from ui.formatters import get_enabled_models, get_model_label_map

def render_composer() -> None:
    """Renders a simplified floating control bar and native chat input element."""
    modes = st.session_state.get("available_modes", ["AUTO", "NEXA_CHAT", "RESEARCH"])
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
                default=st.session_state.selected_mode if st.session_state.selected_mode in modes else "AUTO",
                format_func=lambda x: "✨ Nexa Chat" if x == "NEXA_CHAT" else ("🔬 Deep Research" if x == "RESEARCH" else "🧠 Auto Orchestrate"),
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
                format_func=lambda x: model_label_map.get(x, x if x != "AUTO" else "🤖 Auto Model"),
                key="composer_model",
                label_visibility="collapsed",
            )
            st.session_state.selected_model_id = selected_model

        user_input = st.chat_input(
            placeholder="Ask Nexa anything...",
            disabled=st.session_state.get("is_waiting_for_response", False),
            key="nexa_chat_input",
        )

    if user_input and not st.session_state.get("is_waiting_for_response", False):
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

# path: frontend/ui/composer_ui.py -> process_pending_request function update

def process_pending_request() -> None:
    """Streams tokens in real-time with a clean, responsive 'Thinking' state indicator."""
    pending = st.session_state.get("pending_request")
    if not pending:
        return

    st.session_state.pending_request = None
    accumulated_reply = ""
    
    with st.chat_message("assistant"):
        token_area = st.empty()
        
        # 🟢 VISUAL STATUS ANCHOR: Render a clean status cue before connection overhead
        token_area.markdown("🧠 *Nexa is thinking...*")

        event_stream = call_backend(
            message=pending["message"],
            session_id=pending["session_id"],
            backend_url=pending["backend_url"],
            model_id=pending["model_id"],
            mode=pending["mode"]
        )

        try:
            for event in event_stream:
                event_type = event.get("type")
                
                if event_type == "token":
                    # The moment the first character fragment lands, overwrite the thinking string
                    accumulated_reply += event.get("delta", "")
                    token_area.markdown(accumulated_reply + "▌")
                    
                elif event_type == "error":
                    error_reply = event.get("reply", "💥 Processing pipeline drop out.")
                    token_area.error(error_reply)
                    accumulated_reply = error_reply
                    
        except Exception as e:
            token_area.error(f"💥 Connection failed: {str(e)}")
            accumulated_reply = "💥 Processing pipeline drop out."

        # Flush final clean markdown state without text cursor indicators
        token_area.markdown(accumulated_reply or "...")
        
        # Cache response into local history
        st.session_state.messages.append({"role": "assistant", "content": accumulated_reply})

    st.session_state.is_waiting_for_response = False
    st.rerun()
