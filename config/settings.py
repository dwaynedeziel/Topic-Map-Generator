import os
import streamlit as st


def get_secret(key: str, default: str = "") -> str:
    """Retrieve a secret from Streamlit secrets or environment variables."""
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv(key, default)


# API Keys
ANTHROPIC_API_KEY = get_secret("ANTHROPIC_API_KEY")
TAVILY_API_KEY = get_secret("TAVILY_API_KEY")
GOOGLE_CLIENT_ID = get_secret("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = get_secret("GOOGLE_CLIENT_SECRET")

# Claude model configuration
CLAUDE_MODEL = "claude-sonnet-4-20250514"
CLAUDE_MAX_TOKENS = 16000
CLAUDE_TEMPERATURE = 0.3

# Tavily configuration
TAVILY_SEARCH_DEPTH = "advanced"
TAVILY_MAX_RESULTS = 5
TAVILY_RATE_LIMIT_DELAY = 0.5  # seconds between requests

# Scope definitions
SCOPE_FOCUSED = "Focused (15-25 topics)"
SCOPE_COMPREHENSIVE = "Comprehensive (40-75 topics)"

SCOPE_RANGES = {
    SCOPE_FOCUSED: (15, 25),
    SCOPE_COMPREHENSIVE: (40, 75),
}

# App metadata
APP_TITLE = "Topic Map Generator"
APP_ICON = "\U0001f5fa\ufe0f"
APP_LAYOUT = "wide"
