"""Application settings and dynamic configuration with robust defaults and model normalization."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

# Valid and verified Gemini model names
DEFAULT_GEMINI_MODEL = "gemini-3.5-flash-lite"
DEFAULT_EMBEDDING_MODEL = "models/gemini-embedding-001"
DEFAULT_CHROMA_DIR = "./chroma_db"

MODEL_FALLBACKS = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash",
]

def normalize_model_name(model_name: Optional[str]) -> str:
    """Normalize model names and map invalid or deprecated names to stable equivalents."""
    if not model_name or not model_name.strip():
        return DEFAULT_GEMINI_MODEL
    
    clean = model_name.strip()
    if clean.startswith("models/"):
        clean = clean[len("models/"):]
    # Map deprecated 2.5-flash which Google AI Studio retired for new users
    if clean in ("gemini-2.5-flash", "gemini-2.5-flash-lite"):
        return "gemini-3.5-flash-lite"
    return clean


def normalize_embedding_model_name(emb_name: Optional[str]) -> str:
    """Ensure standard Google embedding model format with models/ prefix."""
    if not emb_name or not emb_name.strip():
        return DEFAULT_EMBEDDING_MODEL
    
    clean = emb_name.strip()
    if not clean.startswith("models/"):
        return f"models/{clean}"
    return clean


def get_secret(name: str, default: Optional[str] = None) -> Optional[str]:
    """Read a setting from Streamlit session state, Streamlit secrets, or environment variables."""
    # 1. Check Streamlit session state (user-provided in UI)
    try:
        import streamlit as st
        if hasattr(st, "session_state"):
            session_val = st.session_state.get(f"user_{name.lower()}") or st.session_state.get(name)
            if session_val and str(session_val).strip() and str(session_val).strip() != "your_gemini_api_key_here":
                return str(session_val).strip()
    except Exception:
        pass

    # 2. Check Streamlit deployment secrets
    try:
        import streamlit as st
        val = st.secrets.get(name)
        if val and str(val).strip() and str(val).strip() not in ("your_gemini_api_key_here", "replace-with-your-gemini-api-key"):
            return str(val).strip()
    except Exception:
        pass

    # 3. Check environment variables
    env_val = os.getenv(name)
    if env_val and env_val.strip() and env_val.strip() not in ("your_gemini_api_key_here", "replace-with-your-gemini-api-key"):
        return env_val.strip()

    return default


class Settings:
    """Dynamic settings wrapper ensuring changes in session state or secrets reflect immediately."""

    @property
    def gemini_api_key(self) -> Optional[str]:
        return get_secret("GEMINI_API_KEY")

    @property
    def gemini_model(self) -> str:
        raw = get_secret("GEMINI_MODEL", DEFAULT_GEMINI_MODEL)
        return normalize_model_name(raw)

    @property
    def gemini_embedding_model(self) -> str:
        raw = get_secret("GEMINI_EMBEDDING_MODEL", DEFAULT_EMBEDDING_MODEL)
        return normalize_embedding_model_name(raw)

    @property
    def chroma_dir(self) -> str:
        return get_secret("CHROMA_DIR", DEFAULT_CHROMA_DIR) or DEFAULT_CHROMA_DIR


settings = Settings()
