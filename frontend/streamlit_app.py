# path: frontend/streamlit_app.py

import streamlit as st
from ui.api_client import ensure_chat_options_loaded
from ui.chat_ui import render_chat_messages
from ui.composer_ui import process_pending_request, render_composer
from ui.sidebar_ui import render_sidebar
from ui.state import init_state
from ui.styles import inject_custom_css

# Global browser canvas and viewport configuration bounds
st.set_page_config(
    page_title="NexusMind",
    page_icon="⧉",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main() -> None:
    """🌊 Central layout orchestrator for the NexusMind agent stream workspace interface."""
    
    # 1. Initialize persistent session keys and fetch server properties
    init_state()                 # Mounts type-safe single-enum keys onto session state
    inject_custom_css()          # Applies dark-mode style overlays and micro-font rules
    render_sidebar()             # Draws file dropzones and operational status checkers
    ensure_chat_options_loaded() # Asynchronously pre-caches model catalogs and active paths

    # 2. Centered layout canvas grid targeting ultra-wide workspace viewports
    _, center_canvas, _ = st.columns([1.2, 5.0, 1.2])
    
    with center_canvas:
        # 3. Synchronized component stack rendering passes
        render_chat_messages()     # Displays text history cards safely out of session records
        render_composer()          # Draws input boxes and dynamic override switches
        process_pending_request()  # Consumes backend SSE packets and triggers UI stream updates

if __name__ == "__main__":
    main()
