# path: frontend/streamlit_app.py
import streamlit as st
from ui.api_client import ensure_chat_options_loaded
from ui.chat_ui import render_chat_messages
from ui.composer_ui import process_pending_request, render_composer
from ui.sidebar_ui import render_sidebar
from ui.state import init_state
from ui.styles import inject_custom_css

# Maintain wide layout configuration profiles for distributed sub-components
st.set_page_config(
    page_title="NexusMind",
    page_icon="⧉",
    layout="wide",
    initial_sidebar_state="expanded",
)


def main() -> None:
    # 1. Initialize core state registers and inject styles
    init_state()
    inject_custom_css()

    # 2. Render operational tracking sidebars
    render_sidebar()
    ensure_chat_options_loaded()

    # 3. Define a focused center grid container layout
    # Creates a perfectly weighted 3-column system to lock the chat feed into an optimal reading width
    _, center_canvas, _ = st.columns([1.2, 5.0, 1.2])

    with center_canvas:
        # Wrap primary visual execution streams inside our optimized width grid layout
        render_chat_messages()
        render_composer()
        process_pending_request()


if __name__ == "__main__":
    main()
