# path: frontend/ui/state.py
import uuid
import streamlit as st

def init_state() -> None:
    """Registers global storage variables without circular structural dependencies."""
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "Hi, I'm Nexa. Ask me about AI/ML topics, engineering problems, or your ingested documents.",
                # 🟢 CLEANED: Kept array footprints minimal for the new non-blocking streaming data flow
                "trace_logs": [], 
                "metrics": {},    
            }
        ]

    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())

    if "backend_url" not in st.session_state:
        st.session_state.backend_url = "http://localhost:8001"  # Port 8001 maps to our refactored uvicorn server

    if "backend_online" not in st.session_state:
        st.session_state.backend_online = None

    if "backend_status_text" not in st.session_state:
        st.session_state.backend_status_text = "Optional: click to check backend connection status."

    # 🟢 ALIGNED WITH NEW ENUM CONSTANTS: 
    # Swapping old arbitrary mode keys for the type-safe fallback strings
    if "selected_mode" not in st.session_state:
        st.session_state.selected_mode = "AUTO"

    if "selected_model_id" not in st.session_state:
        st.session_state.selected_model_id = "AUTO"

    if "available_modes" not in st.session_state:
        st.session_state.available_modes = ["AUTO", "NEXA_CHAT", "RESEARCH"]

    if "model_catalog" not in st.session_state:
        st.session_state.model_catalog = ["AUTO", "LOCAL", "CLOUD"]

    if "options_loaded" not in st.session_state:
        st.session_state.options_loaded = False

    if "options_error" not in st.session_state:
        st.session_state.options_error = ""

    if "composer_prompt" not in st.session_state:
        st.session_state.composer_prompt = ""

    if "composer_model" not in st.session_state:
        st.session_state.composer_model = st.session_state.selected_model_id

    if "pending_request" not in st.session_state:
        st.session_state.pending_request = None

    if "is_waiting_for_response" not in st.session_state:
        st.session_state.is_waiting_for_response = False


def reset_to_new_chat(message: str) -> None:
    """Flushes active keys and spins up an isolated, unique session identifier token."""
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = [{"role": "assistant", "content": message, "trace_logs": [], "metrics": {}}]
    st.session_state.pending_request = None
    st.session_state.is_waiting_for_response = False


def clear_chat(message: str) -> None:
    """Clears message queues cleanly while preserving the active session pipeline identification."""
    st.session_state.messages = [{"role": "assistant", "content": message, "trace_logs": [], "metrics": {}}]
    st.session_state.pending_request = None
    st.session_state.is_waiting_for_response = False
