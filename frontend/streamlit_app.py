# path: frontend/streamlit_app.py

import streamlit as st
from ui.api_client import ensure_chat_options_loaded
from ui.chat_ui import render_chat_messages
from ui.composer_ui import process_pending_request, render_composer
from ui.sidebar_ui import render_sidebar
from ui.state import init_state
from ui.styles import inject_custom_css

st.set_page_config(
    page_title="NexusMind",
    page_icon="⧉",
    layout="wide",
    initial_sidebar_state="expanded",
)

def main() -> None:
    init_state()
    inject_custom_css()
    render_sidebar()
    ensure_chat_options_loaded()

    _, center_canvas, _ = st.columns([1.2, 5.0, 1.2])
    with center_canvas:
        render_chat_messages()
        render_composer()
        process_pending_request()

if __name__ == "__main__":
    main()