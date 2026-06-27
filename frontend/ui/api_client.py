# path: frontend/ui/api_client.py

from typing import Any, Dict, Generator, Tuple
import requests
import json
import httpx
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

        # 🟢 UPDATED: Maps onto the new schema broadcasted by the updated routes.py
        return {
            "default_model_id": data.get("default_model_selection", "AUTO"),
            "default_mode": data.get("default_chat_selection", "AUTO"),
            "available_modes": data.get("available_chat_paths", ["AUTO", "NEXA_CHAT", "RESEARCH"]),
            "available_models": data.get("available_model_tiers", ["AUTO", "LOCAL", "CLOUD"]),
        }
    except Exception as e:
        raise RuntimeError(f"Failed parsing configuration parameters map: {e}")


def ensure_chat_options_loaded() -> None:
    """Safely synchronizes local UI state matrices with server capability lists."""
    if st.session_state.get("options_loaded"):
        return

    try:
        options = fetch_chat_options(st.session_state.backend_url)
        st.session_state.available_modes = options.get("available_modes", ["AUTO", "NEXA_CHAT", "RESEARCH"])
        st.session_state.model_catalog = options.get("available_models", ["AUTO", "LOCAL", "CLOUD"])

        default_mode = options.get("default_mode", "AUTO")
        default_model_id = options.get("default_model_id", "AUTO")

        if st.session_state.selected_mode not in st.session_state.available_modes:
            st.session_state.selected_mode = default_mode

        if st.session_state.selected_model_id not in st.session_state.model_catalog and st.session_state.selected_model_id != "auto":
            st.session_state.selected_model_id = default_model_id

        st.session_state.composer_model = st.session_state.selected_model_id
        st.session_state.options_loaded = True
        st.session_state.options_error = ""
        st.session_state.backend_online = True
    except Exception as e:
        st.session_state.available_modes = ["AUTO", "NEXA_CHAT", "RESEARCH"]
        st.session_state.model_catalog = ["AUTO", "LOCAL", "CLOUD"]
        st.session_state.options_loaded = True
        st.session_state.options_error = str(e)
        st.session_state.backend_online = False


def refresh_chat_options() -> None:
    """Flushes local cache registers to force a full options reload cycle."""
    st.session_state.options_loaded = False
    ensure_chat_options_loaded()


# path: frontend/ui/api_client.py -> Update call_backend wrapper

def call_backend(
    message: str,
    session_id: str,
    backend_url: str,
    model_id: str,
    mode: str,
) -> Generator[Dict[str, Any], None, None]:
    """Yields live JSON payload event blocks chunk-by-chunk without network timeout rules."""
    url = f"{backend_url.rstrip('/')}/api/chat"
    
    norm_chat = "NEXA_CHAT" if mode == "chat" else ("RESEARCH" if mode == "deep_research" else mode)
    norm_model = "CLOUD" if model_id == "cloud" else ("LOCAL" if model_id == "local" else model_id)
    
    payload = {
        "session_id": session_id,
        "message": message,
        "chat_selection": norm_chat,
        "model_selection": norm_model,
    }

    try:
        # 🟢 REMOVED TIME LIMIT: Timeout set to None so Streamlit waits forever for SSE events
        with httpx.stream("POST", url, json=payload, timeout=None) as resp:
            resp.raise_for_status()
            for line in resp.iter_lines():
                if line.startswith("data:"):
                    data_str = line.replace("data:", "").strip()
                    if data_str == "[DONE]":
                        break
                    yield json.loads(data_str)
                    
    except httpx.ConnectError:
        yield {
            "type": "error",
            "reply": "❌ **Network Gateway Connection Error.**\n\nNexa couldn't establish a socket mapping connection route with the FastAPI gateway."
        }
    except Exception as e:
        yield {
            "type": "error",
            "reply": f"💥 **An unexpected processing failure occurred:** `{str(e)}`"
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
