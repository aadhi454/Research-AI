"""Application settings loaded from environment variables or a local .env."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv


load_dotenv()


def _get_streamlit_secret(name: str, default: str | None = None) -> str | None:
    """Read a setting from Streamlit secrets or environment variables."""
    try:
        import streamlit as st

        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass

    value = os.getenv(name)
    return value if value else default


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str | None = _get_streamlit_secret("GEMINI_API_KEY")
    gemini_model: str = (
        _get_streamlit_secret("GEMINI_MODEL", "gemini-2.5-flash")
        or "gemini-2.5-flash"
    )
    gemini_embedding_model: str = (
        _get_streamlit_secret(
            "GEMINI_EMBEDDING_MODEL",
            "models/gemini-embedding-001",
        )
        or "models/gemini-embedding-001"
    )
    chroma_dir: str = _get_streamlit_secret("CHROMA_DIR", "./chroma_db") or "./chroma_db"


settings = Settings()
