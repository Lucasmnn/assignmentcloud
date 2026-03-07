import re
from typing import Optional

import pandas as pd
import requests
import streamlit as st

from config import API_URL, TMDB_API_KEY, CACHE_TTL_MOVIES, CACHE_TTL_TMDB


@st.cache_data(ttl=CACHE_TTL_MOVIES, show_spinner=False)
def fetch_movies() -> pd.DataFrame:
    """Fetch the full movie catalog from local CSV, API, or TMDB fallback."""
    # 1. Try local CSV (Priority as requested)
    local_df = _load_local_csv()
    if local_df is not None:
        return local_df

    # 2. Try configured API
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
            # 3. Fallback to TMDB directly
            if TMDB_API_KEY:
                # Silenced warning for cleaner UI
                return _fetch_movies_direct_tmdb()
            else:
                st.error("❌ No local CSV, API loop detected, and `TMDB_API_KEY` is missing.")
                return pd.DataFrame()

    except requests.RequestException:
        if TMDB_API_KEY:
            return _fetch_movies_direct_tmdb()
        st.error("❌ Error: No local CSV found and API is unreachable.")
        return pd.DataFrame()


def _load_local_csv() -> Optional[pd.DataFrame]:
    """Load and merge local MovieLens-style CSV files."""
    import os
    from pathlib import Path

    # Root directory (one level up from streamlit_app/)
    base_dir = Path(__file__).resolve().parent.parent
    movies_path = base_dir / "ML-20M-movies.csv"
    ratings_path = base_dir / "ml-20M-ratings.csv"

    if not movies_path.exists():
        return None

    try:
        # Load movies
        movies_df = pd.read_csv(movies_path)
        
        # Try to load ratings if available to get avg_rating
        if ratings_path.exists():
            # Optimization: only read required columns
            ratings_df = pd.read_csv(ratings_path, usecols=["movieId", "rating"])
            avg_ratings = ratings_df.groupby("movieId")["rating"].mean().reset_index()
            # If avg_rating already in movies_df, rename it or merge
            if "avg_rating" in movies_df.columns:
                movies_df = movies_df.drop(columns=["avg_rating"])
            movies_df = pd.merge(movies_df, avg_ratings, on="movieId", how="left").rename(columns={"rating": "avg_rating"})
        
        # Ensure schema compliance
        required_cols = ["movieId", "title", "release_year", "avg_rating", "genres", "language"]
        for col in required_cols:
            if col not in movies_df.columns:
                if col == "avg_rating": movies_df[col] = 0.0
                elif col == "genres": movies_df[col] = "Unknown"
                elif col == "language": movies_df[col] = "xx"
                elif col == "release_year": movies_df[col] = 0
        
        movies_df["avg_rating"] = movies_df["avg_rating"].fillna(0.0)
        
        return movies_df[required_cols]
    except Exception as e:
        st.error(f"⚠️ Error loading local CSV: {e}")
        return None


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
