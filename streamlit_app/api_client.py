"""
API client for communicating with the Flask backend.
All data fetching goes through here — the frontend never touches BigQuery directly.
"""

import requests
import streamlit as st
from config import BACKEND_URL


_TIMEOUT_FAST = 8    # autocomplete / health
_TIMEOUT_MED  = 30   # trending / top-rated
_TIMEOUT_SLOW = 60   # recommendations (TMDB poster enrichment adds latency)


@st.cache_data(ttl=60, show_spinner=False)
def autocomplete(query: str) -> list[dict]:
    """Return Elasticsearch autocomplete suggestions for a partial title."""
    if len(query.strip()) < 2:
        return []
    try:
        r = requests.get(
            f"{BACKEND_URL}/autocomplete",
            params={"q": query},
            timeout=_TIMEOUT_FAST,
        )
        r.raise_for_status()
        return r.json()
    except Exception:
        return []


@st.cache_data(ttl=300, show_spinner=False)
def get_trending(limit: int = 24) -> list[dict]:
    """Most-rated movies with TMDB posters."""
    try:
        r = requests.get(
            f"{BACKEND_URL}/trending",
            params={"limit": limit},
            timeout=_TIMEOUT_MED,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"Could not load trending movies: {e}")
        return []


@st.cache_data(ttl=300, show_spinner=False)
def get_top_rated(limit: int = 24) -> list[dict]:
    """Highest-rated movies with TMDB posters."""
    try:
        r = requests.get(
            f"{BACKEND_URL}/top-rated",
            params={"limit": limit},
            timeout=_TIMEOUT_MED,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.warning(f"Could not load top rated movies: {e}")
        return []


def get_recommendations(movie_ids: list[int], top_n: int = 20) -> list[dict]:
    """Cold-start recommendations based on selected movie IDs."""
    try:
        r = requests.post(
            f"{BACKEND_URL}/recommend",
            json={"movie_ids": movie_ids, "top_n": top_n},
            timeout=_TIMEOUT_SLOW,
        )
        r.raise_for_status()
        return r.json()
    except Exception as e:
        st.error(f"Could not load recommendations: {e}")
        return []


def backend_healthy() -> bool:
    """Quick health check for the backend."""
    try:
        r = requests.get(f"{BACKEND_URL}/", timeout=_TIMEOUT_FAST)
        return r.status_code == 200
    except Exception:
        return False
