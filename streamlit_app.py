# filename: frontend/streamlit_app.py

import json
import uuid
from typing import Any, Dict, Generator

import httpx
import requests
import streamlit as st

# ==============================================================================
# 1. PAGE SETUP & CANVAS CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="NexusMind",
    page_icon="⧉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==============================================================================
# 2. CORE SYSTEM INITIALIZATION & STATE MANAGEMENT
# ==============================================================================

def ensure_system_initialized() -> None:
    """Ensures all session attributes and backend catalog profiles are synchronized."""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("session_id", str(uuid.uuid4()))
    st.session_state.setdefault("backend_url", "http://localhost:8001")
    st.session_state.setdefault("is_waiting_for_response", False)
    st.session_state.setdefault("pending_request", None)

    if not st.session_state.get("options_loaded"):
        try:
            url = f"{st.session_state.backend_url.rstrip('/')}/api/chat/options"
            data = requests.get(url, timeout=4).json()
            st.session_state.available_modes = {m["id"]: m["label"] for m in data.get("available_chat_paths", [])}
            st.session_state.model_catalog = {m["id"]: m["label"] for m in data.get("available_model_tiers", [])}
            st.session_state.backend_online = True
        except Exception:
            st.session_state.available_modes = {"AUTO": "🧠 Auto Orchestrate", "NEXA_CHAT": "✨ Nexa Chat", "RESEARCH": "🔬 Deep Research"}
            st.session_state.model_catalog = {"AUTO": "🤖 Auto Model", "LOCAL": "💻 Local Model", "CLOUD": "☁️ Cloud Model"}
            st.session_state.backend_online = False
        
        st.session_state.selected_mode = "AUTO"
        st.session_state.selected_model_id = "AUTO"
        st.session_state.options_loaded = True


def reset_session(message: str, keep_id: bool = False) -> None:
    """Flushes message state histories, optionally generating a fresh unique tracker token."""
    st.session_state.session_id = st.session_state.session_id if keep_id else str(uuid.uuid4())
    st.session_state.messages = [{"role": "assistant", "content": message}] if message else []
    st.session_state.pending_request = None
    st.session_state.is_waiting_for_response = False
    st.rerun()


# ==============================================================================
# 3. BACKEND API SERVICE INFRASTRUCTURE
# ==============================================================================

def call_backend(pending: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
    """Streams data tokens directly out of the connected gateway server router."""
    url = f"{pending['backend_url'].rstrip('/')}/api/chat"
    payload = {
        "session_id": pending["session_id"],
        "message": pending["message"],
        "chat_selection": pending["mode"],
        "model_selection": pending["model_id"],
    }
    try:
        with httpx.stream("POST", url, json=payload, timeout=None) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    if data_str == "[DONE]":
                        break
                    yield json.loads(data_str)
    except Exception as e:
        yield {"type": "error", "reply": f"❌ **Ecosystem Connection Failure:** `{str(e)}`"}


def handle_document_upload(uploaded_file) -> None:
    """Transmits document bytes straight into the active distributed vector workspace pipeline."""
    url = f"{st.session_state.backend_url.rstrip('/')}/api/rag/upload"
    try:
        with st.spinner("Streaming data block..."):
            files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
            response = requests.post(url, files=files, timeout=60).json()
        
        if response.get("status") == "queued":
            st.success(f"**{uploaded_file.name}** processed successfully!")
        else:
            st.error(f"Blocked: {response.get('message', 'Unknown error')}")
    except Exception as e:
        st.error(f"Ingestion interface fault: {e}")


# ==============================================================================
# 4. PRESENTATION LAYOUT & CUSTOM HTML COMPONENTS
# ==============================================================================

def inject_minimal_overrides() -> None:
    """Transforms standard elements into a high-end, seamless Gemini layout configuration."""
    st.markdown(
        """
        <style>
        /* 1. Message Bubble Custom Elements Layout */
        .chat-row { display: flex; width: 100%; margin-bottom: 1.25rem; }
        .user-row { justify-content: flex-end; }
        
        .user-bubble {
            background-color: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.2);
            border-radius: 1.25rem;
            padding: 0.65rem 1.1rem;
            max-width: 75%;
            width: fit-content;
            color: var(--text-color);
        }
        
        .bot-bubble {
            font-size: 1rem;
            line-height: 1.6;
            max-width: 100%;
            color: var(--text-color);
            padding: 0.5rem 0rem;
        }
        
        /* 2. Forces bottom row header columns block to lock at exactly 720px width */
        div.stHorizontalBlock:has(div[data-testid="stSelectbox"]) {
            max-width: 720px !important;
            width: 720px !important;
            margin: 0 auto !important;
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            gap: 16px !important;
        }
        
        div.stHorizontalBlock:has(div[data-testid="stSelectbox"]) > div {
            width: auto !important;
            flex: unset !important;
            min-width: unset !important;
        }

        /* 3. Dropdown Width & Flex Vertical Centering Mechanics */
        div[data-testid="stSelectbox"] {
            width: max-content !important;
            min-width: 185px !important;
            max-width: 280px !important;
            flex-grow: 0 !important;
        }
        
        div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div {
            border-radius: 999px !important;
            padding: 0px 4px 0px 10px !important;
            min-height: 28px !important;
            height: 28px !important;
            background-color: rgba(128, 128, 128, 0.05) !important;
            border: 1px solid rgba(128, 128, 128, 0.12) !important;
            transition: all 0.2s ease;
            display: flex !important;
            align-items: center !important;
        }
        
        div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div:hover {
            background-color: rgba(128, 128, 128, 0.09) !important;
            border-color: rgba(128, 128, 128, 0.25) !important;
        }

        /* 4. Fine-Tuned Clean Sans-Serif Typography with Neutral Alignment */
        div[data-testid="stSelectbox"] div[data-placeholder],
        div[data-testid="stSelectbox"] [data-testid="stMarkdownContainer"] p,
        div[data-testid="stSelectbox"] span,
        div[data-testid="stSelectbox"] div {
            font-family: Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
            font-size: 0.78rem !important;
            font-weight: 500 !important;
            line-height: normal !important;
            text-overflow: unset !important;
            white-space: nowrap !important;
            overflow: visible !important;
            display: inline-flex !important;
            align-items: center !important;
        }

        div[data-testid="stSelectbox"] svg {
            top: unset !important;
        }

        /* 5. Single-Frame Capsule Chat Input Container */
        div[data-testid="stChatInput"] {
            border-radius: 1.5rem !important;
            background-color: rgba(128, 128, 128, 0.04) !important;
            border: 1px solid rgba(128, 128, 128, 0.15) !important;
            padding: 0.25rem 0.5rem !important;
            box-shadow: none !important;
            max-width: 720px !important;
            margin-left: auto !important;
            margin-right: auto !important;
            margin-top: 6px !important;
            transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
        }
        
        div[data-testid="stChatInput"]:focus-within {
            border-color: rgba(99, 102, 241, 0.35) !important;
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.06) !important;
        }

        div[data-testid="stChatInput"] > div,
        div[data-testid="stChatInput"] [data-tight="true"],
        div[data-testid="stChatInput"] textarea {
            background-color: transparent !important;
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }

        div[data-testid="stChatInput"] textarea {
            font-size: 0.92rem !important;
            color: var(--text-color) !important;
            padding-top: 0.45rem !important;
        }

        /* Rounded Action Send Button Controls */
        div[data-testid="stChatInput"] button {
            border-radius: 999px !important;
            background-color: transparent !important;
            height: 32px !important;
            width: 32px !important;
        }
        
        div[data-testid="stChatInput"] button:hover {
            background-color: rgba(128, 128, 128, 0.08) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_message_bubble(role: str, content: str) -> None:
    """Renders a clean text layout block that wraps exactly to content bounds."""
    if role == "user":
        st.markdown(
            f'<div class="chat-row user-row"><div class="user-bubble">{content}</div></div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown('<div class="bot-bubble">', unsafe_allow_html=True)
        st.markdown(content)
        st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar() -> None:
    """Renders application controllers, dynamic status maps, and data managers."""
    with st.sidebar:
        st.subheader("⧉ NexusMind")
        
        status_lbl, color = ("CONNECTED", "green") if st.session_state.backend_online else ("OFFLINE", "orange")
        st.caption(f"Engine Status: :{color}[● {status_lbl}]")

        c1, c2 = st.columns(2)
        if c1.button("✨ New Session", use_container_width=True):
            reset_session(message="")
        if c2.button("🗑️ Reset", use_container_width=True):
            reset_session(message="", keep_id=True)

        if st.button("🔌 Ping Host Cluster", use_container_width=True):
            st.session_state.options_loaded = False
            st.rerun()

        st.divider()
        st.caption("**SESSION CORE IDENTITY**")
        st.code(st.session_state.session_id, language=None)
        
        st.divider()
        st.caption("**DATA SOURCE MANAGEMENT**")
        with st.expander("📥 Ingest Reference Files (RAG)", expanded=False):
            uploaded = st.file_uploader("Select Reference PDF", type=["pdf"], label_visibility="collapsed", key="sidebar_rag")
            if uploaded:
                handle_document_upload(uploaded)


def render_chat_interface() -> None:
    """Manages conversational historical grids with a clean Gemini bottom selector tray."""
    messages = st.session_state.get("messages", [])
    
    if not any(msg.get("role") == "user" for msg in messages):
        st.markdown(
            "<div style='text-align: center; margin-top: 6vh; margin-bottom: 4vh;'>"
            "<span style='font-family: monospace; font-size: 0.8rem; color: #6366F1; font-weight: 600; letter-spacing: 1px;'>NEXUS // CORE</span>"
            "<h2 style='margin: 5px 0;'>Ask anything. Research deeply.</h2>"
            "<p style='opacity: 0.6; font-size: 0.85rem;'>A streamlined engineering workspace for unified study.</p>"
            "</div>", 
            unsafe_allow_html=True
        )

    for msg in messages:
        render_message_bubble(role=msg["role"], content=msg["content"])

    with st.bottom:
        col_selectors = st.columns(2)
        
        with col_selectors[0]:
            mode_options = list(st.session_state.available_modes.keys())
            current_mode = st.session_state.selected_mode
            selected_mode_id = st.selectbox(
                "Mode", options=mode_options,
                index=mode_options.index(current_mode) if current_mode in mode_options else 0,
                format_func=lambda x: st.session_state.available_modes.get(x, x),
                label_visibility="collapsed", key="mode_select"
            )
            if selected_mode_id:
                st.session_state.selected_mode = selected_mode_id

        with col_selectors[1]:
            model_options = list(st.session_state.model_catalog.keys())
            current_model = st.session_state.selected_model_id
            selected_model_id = st.selectbox(
                "Model", options=model_options,
                index=model_options.index(current_model) if current_model in model_options else 0,
                format_func=lambda x: st.session_state.model_catalog.get(x, x),
                label_visibility="collapsed", key="model_select"
            )
            if selected_model_id:
                st.session_state.selected_model_id = selected_model_id

        user_input = st.chat_input("Ask Nexa anything...", disabled=st.session_state.is_waiting_for_response)

    if user_input and not st.session_state.is_waiting_for_response:
        clean_input = user_input.strip()
        if clean_input:
            st.session_state.messages.append({"role": "user", "content": clean_input})
            st.session_state.pending_request = {
                "message": clean_input, "session_id": st.session_state.session_id,
                "backend_url": st.session_state.backend_url, "model_id": st.session_state.selected_model_id,
                "mode": st.session_state.selected_mode,
            }
            st.session_state.is_waiting_for_response = True
            st.rerun()


def process_pending_request() -> None:
    """Processes incoming chunks cleanly inside real-time display contexts."""
    pending = st.session_state.get("pending_request")
    if not pending:
        return

    st.session_state.pending_request = None
    accumulated_reply = ""
    
    status_container = st.empty()
    status_container.markdown(
        "<div style='display: flex; align-items: center; gap: 8px; margin-top: 5px; opacity: 0.65; font-size: 0.85rem; font-family: monospace; margin-left: auto; margin-right: auto; max-width: 720px;'>"
        "<i>Nexa is thinking...</i>"
        "</div>", 
        unsafe_allow_html=True
    )

    try:
        backend_stream = call_backend(pending)
        token_area = None
        
        for event in backend_stream:
            if event.get("type") == "token":
                if not accumulated_reply:
                    status_container.empty()
                    st.markdown('<div class="bot-bubble">', unsafe_allow_html=True)
                    token_area = st.empty()

                accumulated_reply += event.get("delta", "")
                if token_area:
                    token_area.markdown(accumulated_reply + "▌")
                
            elif event.get("type") == "error":
                status_container.empty()
                accumulated_reply = event.get("reply", "💥 Processing pipeline drop out.")
                st.error(accumulated_reply)
                break
                
    except Exception as e:
        status_container.empty()
        accumulated_reply = f"💥 Connection failed: {str(e)}"
        st.error(accumulated_reply)

    if accumulated_reply and not accumulated_reply.startswith("💥"):
        st.markdown('</div>', unsafe_allow_html=True)
        status_container.empty()
        if token_area:
            token_area.markdown(accumulated_reply)
        st.session_state.messages.append({"role": "assistant", "content": accumulated_reply})

    st.session_state.is_waiting_for_response = False
    st.rerun()


# ==============================================================================
# 5. MAIN CENTRAL APP LAYOUT ORCHESTRATOR
# ==============================================================================

def main() -> None:
    """Main execution entry point targeting wide layout viewports."""
    ensure_system_initialized()
    inject_minimal_overrides()
    render_sidebar()

    _, center_canvas, _ = st.columns([1.2, 5.0, 1.2])
    
    with center_canvas:
        render_chat_interface()
        process_pending_request()

if __name__ == "__main__":
    main()