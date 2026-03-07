import re
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from config import API_URL, TMDB_API_KEY, CACHE_TTL_MOVIES, CACHE_TTL_TMDB


@st.cache_data(ttl=CACHE_TTL_MOVIES, show_spinner=False)
def fetch_movies() -> pd.DataFrame:
    """Fetch the full movie catalog from the backend Cloud Function.

    Returns:
        A DataFrame with columns such as ``movieId``, ``title``,
        ``release_year``, ``avg_rating``, ``genres``, ``language``.
        Returns an empty DataFrame on failure.
    """
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        
        try:
            data = response.json()
        except ValueError as json_err:
            content_snippet = response.text[:200].replace("\n", " ")
            st.error(f"❌ API returned non-JSON data (Content-Type: {response.headers.get('Content-Type')})")
            st.info(f"Snippet: {content_snippet}...")
            return pd.DataFrame()

        if isinstance(data, dict) and "movie_details" in data:
            data = data["movie_details"]

        df = pd.DataFrame(data)
        return df

    except requests.RequestException as e:
        st.error(f"❌ Error fetching data from API: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=CACHE_TTL_TMDB, show_spinner=False)
def fetch_tmdb_details(title: str, year: int) -> Optional[dict]:
    """Search TMDB for movie details and poster by title and year.

    Args:
        title: Movie title (may contain parenthetical info).
        year: Release year of the movie.

    Returns:
        A dict with TMDB movie details (poster_path, overview, tagline, …),
        or ``None`` if the key is missing or the search fails.
    """
    if not TMDB_API_KEY:
        return None

    try:

        clean_title = re.sub(r"\s*\(.*?\)\s*", " ", title).strip()

        search_url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": TMDB_API_KEY, "query": clean_title, "year": int(year)}
        resp = requests.get(search_url, params=params, timeout=10)
        resp.raise_for_status()
        results = resp.json().get("results", [])

        if not results:
            # Retry without year constraint
            params.pop("year", None)
            resp = requests.get(search_url, params=params, timeout=10)
            resp.raise_for_status()
            results = resp.json().get("results", [])

        if not results:
            return None

        tmdb_id = results[0]["id"]


        detail_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        detail_resp = requests.get(
            detail_url, params={"api_key": TMDB_API_KEY}, timeout=10
        )
        detail_resp.raise_for_status()
        return detail_resp.json()

    except Exception:
        return None
