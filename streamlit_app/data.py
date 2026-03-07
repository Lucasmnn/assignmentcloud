import re
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from config import API_URL, TMDB_API_KEY, CACHE_TTL_MOVIES, CACHE_TTL_TMDB


@st.cache_data(ttl=CACHE_TTL_MOVIES, show_spinner=False)
def fetch_movies() -> pd.DataFrame:
    """Fetch the full movie catalog from the BigQuery-backed API or TMDB fallback."""
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        
        try:
            data = response.json()
            if isinstance(data, dict) and "movie_details" in data:
                data = data["movie_details"]
            df = pd.DataFrame(data)
            
            if not df.empty:
                # Format for frontend (Rating 0-10 -> 0-5, Genre ID -> Names)
                return _format_catalog_data(df)
            return df
            
        except ValueError:
            # Fallback to TMDB directly
            if TMDB_API_KEY:
                # Silenced warning for cleaner UI
                return _fetch_movies_direct_tmdb()
            else:
                st.error("❌ API loop detected and `TMDB_API_KEY` is missing.")
                return pd.DataFrame()

    except requests.RequestException:
        if TMDB_API_KEY:
            return _fetch_movies_direct_tmdb()
        st.error("❌ Error: API is unreachable and no TMDB fallback available.")
        return pd.DataFrame()


def _format_catalog_data(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize ratings and map genre IDs to names for consistent display."""
    # TMDB Genre ID to Name mapping (standard TMDB IDs)
    GENRE_MAP = {
        28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy",
        80: "Crime", 99: "Documentary", 18: "Drama", 10751: "Family",
        14: "Fantasy", 36: "History", 27: "Horror", 10402: "Music",
        9648: "Mystery", 10749: "Romance", 878: "Sci-Fi", 10770: "TV Movie",
        53: "Thriller", 10752: "War", 37: "Western",
        # ML-20M custom genres (common mappings)
        "Action": "Action", "Adventure": "Adventure", "Animation": "Animation",
        "Children": "Children", "Comedy": "Comedy", "Crime": "Crime",
        "Documentary": "Documentary", "Drama": "Drama", "Fantasy": "Fantasy",
        "Film-Noir": "Film-Noir", "Horror": "Horror", "Musical": "Musical",
        "Mystery": "Mystery", "Romance": "Romance", "Sci-Fi": "Sci-Fi",
        "Thriller": "Thriller", "War": "War", "Western": "Western"
    }

    def _map_genres(g_str):
        if not g_str or pd.isna(g_str): return "Unknown"
        # Handle both list of IDs (from TMDB) and pipe-separated names (from BigQuery)
        parts = str(g_str).split("|")
        mapped = []
        for p in parts:
            try:
                # If numeric string, map ID
                gid = int(p)
                mapped.append(GENRE_MAP.get(gid, p))
            except ValueError:
                # If name string, use as is (or map for consistency)
                mapped.append(GENRE_MAP.get(p, p))
        return "|".join(dict.fromkeys(mapped)) # Deduplicate

    # Ratings: Normalize to 5-star scale if values look like 0-10 or 0-20
    if not df.empty and df["avg_rating"].max() > 5.1:
        # If max is > 10, it might be 0-100 or something else, but 0-10 is most common
        scale_factor = 20.0 if df["avg_rating"].max() > 10.1 else 2.0
        df["avg_rating"] = df["avg_rating"] / scale_factor

    df["genres"] = df["genres"].apply(_map_genres)
    
    # Final safety deduplication
    return df.drop_duplicates(subset=["movieId"])


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
