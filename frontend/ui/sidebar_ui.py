# path: frontend/ui/sidebar_ui.py

import streamlit as st
from ui.api_client import (
    check_backend_status,
    refresh_chat_options,
    upload_document_stream,
)
from ui.state import clear_chat, reset_to_new_chat

def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <style>
                [data-testid="stSidebarUserContent"] { padding-top: 1.5rem !important; padding-bottom: 1.5rem !important; }
                .sb-logo-container { display: inline-flex; align-items: center; gap: 8px; margin-bottom: -2px; }
                .sb-logo-icon { color: #6366F1; font-weight: 800; font-family: monospace; font-size: 1.25rem; letter-spacing: -1px; }
                .sb-header { font-weight: 700; font-size: 1.05rem; letter-spacing: 0.5px; font-family: 'SFMono-Regular', Consolas, monospace; color: rgba(255, 255, 255, 0.95); }
                @media (prefers-color-scheme: light) { .sb-header { color: rgba(0, 0, 0, 0.95); } }
                .sb-caption { font-size: 0.72rem; opacity: 0.5; font-family: sans-serif; }
                .sb-status-line { font-size: 0.72rem; font-family: monospace; display: inline-flex; align-items: center; gap: 5px; }
                .dot { width: 6px; height: 6px; border-radius: 50%; display: inline-block; }
                .dot-online { background-color: #38A169; box-shadow: 0 0 6px #38A169; }
                .dot-warning { background-color: #DD6B20; box-shadow: 0 0 6px #DD6B20; }
                .sb-meta-text { font-family: monospace; font-size: 0.70rem; font-weight: 600; opacity: 0.4; letter-spacing: 0.5px; margin-top: 4px; margin-bottom: 4px; }
                div[data-testid="stExpander"] { margin-bottom: 4px !important; }
                .stButton > button { font-size: 0.75rem !important; padding: 2px 8px !important; min-height: 28px !important; font-family: monospace !important; }
                hr { margin-top: 0.75rem !important; margin-bottom: 0.75rem !important; opacity: 0.15 !important; }
                .guide-header { font-family: monospace; font-size: 0.72rem; font-weight: bold; margin-top: 6px; color: #6366F1; }
                .guide-text { font-size: 0.70rem; opacity: 0.7; line-height: 1.3; margin-bottom: 4px; }
                .sb-flow-footer { margin-top: 1.5rem; font-family: monospace; font-size: 0.68rem; opacity: 0.35; display: flex; justify-content: space-between; }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class='sb-logo-container'>
                <span class='sb-logo-icon'>⧉</span>
                <span class='sb-header'>NexusMind</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "backend_online" not in st.session_state or st.session_state.backend_online is None:
            is_online, _ = check_backend_status(st.session_state.get("backend_url", ""))
            st.session_state.backend_online = is_online

        dot_class, status_lbl = ("dot-online", "CONNECTED") if st.session_state.backend_online else ("dot-warning", "OFFLINE")

        st.markdown(
            f"""
            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;'>
                <span class='sb-caption'>Engineering Compute Engine</span>
                <span class='sb-status-line'><span class='dot {dot_class}'></span>{status_lbl}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Action Group Buttons
        col_chat, col_clear = st.columns(2)
        with col_chat:
            if st.button("✨ New Session", use_container_width=True):
                reset_to_new_chat("Initialized fresh core environment instance.")
                st.rerun()
        with col_clear:
            if st.button("🗑️ Reset", use_container_width=True):
                clear_chat("Session history dropped.")
                st.rerun()

        col_check, col_sync = st.columns(2)
        with col_check:
            if st.button("🔌 Ping Host", use_container_width=True, help="Ping backend endpoint clusters"):
                is_online, status_text = check_backend_status(st.session_state.backend_url)
                st.session_state.backend_online = is_online
                st.session_state.backend_status_text = status_text
                st.rerun()
        with col_sync:
            if st.button("🔄 Sync Models", use_container_width=True, help="Force reload configuration models"):
                refresh_chat_options()
                st.rerun()

        st.divider()

        st.markdown("<p class='sb-meta-text' style='margin-bottom: 2px;'>SESSION IDENTITY IDENTIFIER</p>", unsafe_allow_html=True)
        col_id, col_copy = st.columns([4, 1])
        with col_id:
            st.code(st.session_state.session_id, language=None)
        with col_copy:
            if st.button("📋", help="Copy tracking token reference"):
                st.toast("Session ID token copied!", icon="✅")

        st.divider()

        st.markdown("<p class='sb-meta-text'>DOCUMENTATION & SYSTEM GUIDE</p>", unsafe_allow_html=True)
        with st.expander("💡 Operations Manual & Trace Matrix", expanded=False):
            st.markdown("<div class='guide-header'>🔍 TELEMETRY GLOSSARY</div>", unsafe_allow_html=True)
            st.markdown("<div class='guide-text'><b>🤖 Standard Assistant</b>: Fast, localized execution on local hardware.<br/><b>🔷 Deep Analysis</b>: Triggers multi-query parallel vector checking.<br/><b>⚡ Dynamic Route</b>: Automated backend scaling activated for accuracy.</div>", unsafe_allow_html=True)

        st.divider()

        st.markdown("<p class='sb-meta-text'>DATA SOURCE MANAGEMENT</p>", unsafe_allow_html=True)
        with st.expander("📥 Ingest Reference Files (RAG)", expanded=False):
            uploaded_file = st.file_uploader(
                "Select Engineering Reference File",
                type=["pdf"],
                label_visibility="collapsed",
                key="sidebar_rag_uploader",
            )

            if uploaded_file:
                with st.spinner("Streaming data block..."):
                    response = upload_document_stream(st.session_state.backend_url, uploaded_file)

                if response.get("status") == "queued":
                    st.success(f"**{uploaded_file.name}** processing!")
                    st.caption("Background vector workers active.")
                else:
                    st.error(f"Blocked: {response.get('message', 'Unknown error')}")
                refresh_chat_options()

        st.divider()
        st.markdown("<div class='sb-flow-footer'><span>BUILD v2.0.0</span><span>NexusMind Workspace</span></div>", unsafe_allow_html=True)