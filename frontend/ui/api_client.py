# path: frontend/ui/api_client.py

from typing import Any, Dict, Tuple
import requests
import streamlit as st

def check_backend_status(backend_url: str) -> Tuple[bool, str]:
    """Pings health check endpoints to assess backend connectivity status."""
    base_url = backend_url.rstrip("/")
    if base_url.endswith("/api"):
        health_url = base_url.replace("/api", "/health")
    else:
        health_url = f"{base_url}/health"

    try:
        resp = requests.get(health_url, timeout=3)
        if resp.ok:
            return True, "Connected to backend platform context daemon."
    except Exception:
        pass

    return False, "Backend is unreachable right now."


def fetch_chat_options(backend_url: str) -> Dict[str, Any]:
    """Queries configuration parameters from the core FastAPI gateway server."""
    url = f"{backend_url.rstrip('/')}/api/chat/options"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return {
            "default_model_id": data.get("default_model_id", "auto"),
            "default_mode": data.get("default_mode", "chat"),
            "available_modes": data.get("available_modes", ["chat", "deep_research"]),
            "available_models": data.get("available_models", []),
        }
    except Exception as e:
        raise RuntimeError(f"Failed parsing configuration parameters map: {e}")


def ensure_chat_options_loaded() -> None:
    """Safely synchronizes local UI state matrices with server capability lists."""
    if st.session_state.get("options_loaded"):
        return

    try:
        options = fetch_chat_options(st.session_state.backend_url)
        st.session_state.available_modes = options.get("available_modes", ["chat", "deep_research"])
        st.session_state.model_catalog = options.get("available_models", [])

        default_mode = options.get("default_mode", "chat")
        default_model_id = options.get("default_model_id", "auto")

        if st.session_state.selected_mode not in st.session_state.available_modes:
            st.session_state.selected_mode = default_mode

        if st.session_state.selected_model_id not in st.session_state.model_catalog and st.session_state.selected_model_id != "auto":
            st.session_state.selected_model_id = default_model_id

        st.session_state.composer_model = st.session_state.selected_model_id
        st.session_state.options_loaded = True
        st.session_state.options_error = ""
        st.session_state.backend_online = True
    except Exception as e:
        st.session_state.available_modes = ["chat", "deep_research"]
        st.session_state.model_catalog = []
        st.session_state.options_loaded = True
        st.session_state.options_error = str(e)
        st.session_state.backend_online = False


def refresh_chat_options() -> None:
    """Flushes local cache registers to force a full options reload cycle."""
    st.session_state.options_loaded = False
    ensure_chat_options_loaded()


def call_backend(
    message: str,
    session_id: str,
    backend_url: str,
    model_id: str,
    mode: str,
) -> Dict[str, Any]:
    """Executes a POST request to the unified routing network endpoint."""
    url = f"{backend_url.rstrip('/')}/api/chat"
    payload = {
        "session_id": session_id,
        "message": message,
        "model_id": model_id,
        "mode": mode,
    }

    try:
        resp = requests.post(url, json=payload, timeout=300)
        resp.raise_for_status()
        data = resp.json()

        return {
            "reply": data.get("reply", "Sorry, I did not receive a valid response block."),
            "trace_logs": data.get("trace_logs", []),
            "metrics": data.get("metrics", {})
        }
    except requests.exceptions.Timeout:
        return {
            "reply": "⚠️ **The backend system processing lifecycle timed out.**\n\nYour deep research or reasoning query exceeded the maximum generation window constraint limit (300 seconds).",
            "trace_logs": [],
            "metrics": {},
        }
    except requests.exceptions.ConnectionError:
        return {
            "reply": "❌ **Network Gateway Connection Error.**\n\nNexa couldn't establish a socket mapping connection route with the FastAPI gateway.",
            "trace_logs": [],
            "metrics": {},
        }
    except Exception as e:
        return {
            "reply": f"💥 **An unexpected processing failure occurred:** `{str(e)}`",
            "trace_logs": [],
            "metrics": {},
        }


def upload_document_stream(backend_url: str, uploaded_file) -> Dict[str, Any]:
    """Transmits a raw file binary buffer payload to the background RAG pipeline."""
    url = f"{backend_url.rstrip('/')}/api/rag/upload"
    try:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        resp = requests.post(url, files=files, timeout=60)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {
            "status": "error",
            "message": f"Ingestion stream pipeline failure interface fault: {e}",
        }