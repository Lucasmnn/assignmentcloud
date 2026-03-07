import re
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from config import API_URL, TMDB_API_KEY, CACHE_TTL_MOVIES, CACHE_TTL_TMDB


@st.cache_data(ttl=CACHE_TTL_MOVIES, show_spinner=False)
def fetch_movies() -> pd.DataFrame:
    """Fetch the full movie catalog from the backend Cloud Function or TMDB fallback."""
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        
        try:
            data = response.json()
            if isinstance(data, dict) and "movie_details" in data:
                data = data["movie_details"]
            df = pd.DataFrame(data)
            return df.drop_duplicates(subset=["movieId"]) if not df.empty else df
            
        except ValueError:
            # Fallback: If API returns HTML (loop/IAP), try direct TMDB fetch
            if TMDB_API_KEY:
                # Silenced warning as requested by user for cleaner UI
                return _fetch_movies_direct_tmdb()
            else:
                st.error("❌ API_URL returned HTML (Self-loop) and `TMDB_API_KEY` is missing from environment or .env.")
                return pd.DataFrame()

    except requests.RequestException as e:
        if TMDB_API_KEY:
            st.warning(f"⚠️ API unreachable ({e}). Falling back to direct TMDB fetch.")
            return _fetch_movies_direct_tmdb()
        st.error(f"❌ Error fetching data from API: {e}")
        return pd.DataFrame()


def _fetch_movies_direct_tmdb() -> pd.DataFrame:
    """Fallback logic to populate the catalog directly from TMDB discover."""
    # TMDB Genre ID to Name mapping
    GENRE_MAP = {
        28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
        80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
        14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
        9648: "Mystery", 10749: "Romance", 878: "Sci-Fi", 10770: "TV Movie",
        53: "Thriller", 10752: "War", 37: "Western"
    }

    try:
        url = "https://api.themoviedb.org/3/discover/movie"
        all_results = []
        # Fetch 10 pages for a larger catalog (~200 movies)
        for page in range(1, 11):
            resp = requests.get(
                url, 
                params={"api_key": TMDB_API_KEY, "page": page, "sort_by": "popularity.desc"}, 
                timeout=10
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            all_results.extend(results)
        
        # Transform TMDB results to match the app's expected schema
        movies = []
        for m in all_results:
            # TMDB uses 0-10 scale, app uses 0-5
            normalized_rating = m.get("vote_average", 0.0) / 2.0
            
            # Map genre IDs to names
            genre_ids = m.get("genre_ids", [])
            genre_names = [GENRE_MAP.get(gid, str(gid)) for gid in genre_ids]
            
            movies.append({
                "movieId": m["id"],
                "title": m["title"],
                "release_year": int(m["release_date"][:4]) if m.get("release_date") else 0,
                "avg_rating": normalized_rating,
                "genres": "|".join(genre_names),
                "language": m.get("original_language", "xx")
            })
        df = pd.DataFrame(movies)
        return df.drop_duplicates(subset=["movieId"]) if not df.empty else df
    except Exception as e:
        st.error(f"❌ Fallback fetch failed: {e}")
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
