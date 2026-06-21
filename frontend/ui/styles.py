# path: frontend/ui/styles.py
import streamlit as st


def inject_custom_css() -> None:
    """Injects a minimalist, high-density design system into Streamlit."""
    st.markdown(
        """
        <style>
        /* 1. HERO CANVAS & LANDING STYLING */
        .nexa-hero {
            padding-top: 0.5rem;
            padding-bottom: 0.5rem;
        }
        .nexa-eyebrow {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            border-radius: 999px;
            background: rgba(99, 102, 241, 0.12);
            color: #6366F1;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.75rem;
        }
        .nexa-title {
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1.1;
            letter-spacing: -0.02em;
            margin-bottom: 0.5rem;
            color: var(--text-color);
        }
        .nexa-subtitle {
            font-size: 0.95rem;
            color: var(--text-color);
            opacity: 0.80;
            max-width: 680px;
            margin: 0 auto 0.5rem auto;
        }
        .nexa-muted {
            font-size: 0.85rem;
            color: var(--text-color);
            opacity: 0.55;
        }

        /* 2. HIGH-DENSITY SIDEBAR OVERRIDES */
        [data-testid="stSidebarUserContent"] {
            padding: 1.5rem 1rem 1rem 1rem !important;
        }

        /* 3. MODERN CHAT BUBBLE ENGINE */
        div[data-testid="stChatMessage"] {
            border-radius: 0.5rem;
            margin-bottom: 0.4rem;
            background-color: transparent !important;
        }

        /* User Bubble */
        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
            flex-direction: row-reverse;
        }
        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
            margin-left: auto;
            margin-right: 0;
            max-width: 75%;
            background: rgba(99, 102, 241, 0.12);
            border: 1px solid rgba(99, 102, 241, 0.2);
            padding: 0.65rem 1rem;
            border-radius: 1rem 1rem 0.25rem 1rem;
        }

        /* Assistant Bubble - Expanded to 92% for complex logs/code */
        div[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) [data-testid="stChatMessageContent"] {
            margin-left: 0;
            margin-right: auto;
            max-width: 92%; 
            background: rgba(128, 128, 128, 0.06);
            border: 1px solid rgba(128, 128, 128, 0.12);
            padding: 0.75rem 1.1rem;
            border-radius: 1rem 1rem 1rem 0.25rem;
            color: var(--text-color);
        }

        /* 4. COMPOSER PILLS ACTIVE ACCENT GLOW */
        div[data-testid="stBaseButton-pill"] button[aria-checked="true"] {
            background-color: rgba(99, 102, 241, 0.15) !important;
            border: 1px solid #6366F1 !important;
            color: #6366F1 !important;
            font-weight: 600 !important;
        }

        /* 5. MONOSPACED TRACE HEADERS */
        div[data-testid="stExpander"] details summary p {
            font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace !important;
            font-size: 0.8rem !important;
            color: var(--text-color) !important;
            opacity: 0.85;
        }

        /* Clean up unused legacy form containers borders */
        div[data-testid="stForm"] { border: none !important; padding: 0 !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )
