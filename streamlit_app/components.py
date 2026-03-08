from typing import Optional
import pandas as pd
import streamlit as st
from config import TMDB_API_KEY, TMDB_IMG_BASE, TMDB_IMG_SMALL
from data import fetch_tmdb_details
from utils import get_genre_class, get_language_label, render_stars

def render_landing_page() -> None:
    st.markdown(
        """
        <div class="landing-container">
            <div class="landing-content">
                <div style="font-family: 'Outfit', sans-serif; color: #8b8ba7; font-weight: 600; text-transform: uppercase;">HEC Lausanne</div>
                <div class="landing-logo">Unil.</div>
                <div class="landing-subtitle">Assigment numero 1</div>
                <div class="landing-description">Explore the vast universe of 27,000+ movies directly from BigQuery.</div>
                <div class="landing-btn">
        """,
        unsafe_allow_html=True,
    )
    if st.button("🚀 Enter Library", key="enter_btn"):
        st.session_state.entered = True
        st.rerun()
    st.markdown("</div></div></div>", unsafe_allow_html=True)

def render_main_search_bar(df: pd.DataFrame) -> str:
    all_titles = sorted(df["title"].dropna().unique().tolist())
    st.markdown('<div class="main-search-container"><div class="search-title">🔍 Discover Your Next Movie</div>', unsafe_allow_html=True)
    search_title = st.selectbox("Search", options=[""] + all_titles, index=0, placeholder="Type to search...", label_visibility="collapsed", key="filt_t")
    st.markdown("</div>", unsafe_allow_html=True)
    return search_title

def render_movie_card_html(movie: pd.Series) -> str:
    genres = str(movie.get("genres", "")).split("|")
    genres = [g.strip() for g in genres if g.strip() and g != "(no genres listed)"][:3]
    genre_tags = "".join(f'<span class="genre-tag">{g}</span>' for g in genres)
    return f"""
    <div class="movie-card">
        <div class="movie-title">{movie.get("title", "Unknown")}</div>
        <div class="movie-year">📅 {int(movie.get("release_year", 0))}</div>
        <div class="movie-meta-tags">
            <span class="tag tag-rating">⭐ {movie.get("avg_rating", 0):.1f}/5</span>
            <span class="tag tag-lang">🌐 {movie.get("language", "en").upper()}</span>
        </div>
        <div class="genre-tag-list">{genre_tags}</div>
    </div>
    """

def show_detail_view(movie_row, df) -> None:
    if st.button("← Back"):
        st.session_state.pop("selected_movie", None)
        st.rerun()
    tmdb = fetch_tmdb_details(movie_row["title"], int(movie_row["release_year"]))
    col1, col2 = st.columns([1, 2])
    with col1:
        if tmdb and tmdb.get("poster_path"): st.image(f"{TMDB_IMG_BASE}{tmdb['poster_path']}")
        else: st.markdown('<div style="height:400px; background:#222; border-radius:10px;"></div>', unsafe_allow_html=True)
    with col2:
        st.title(movie_row["title"])
        st.write(tmdb.get("overview") if tmdb else "No synopsis available.")

def render_metrics(df, filtered, g_count) -> None:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🎞️ Library", f"{len(df):,}")
    c2.metric("🔎 Matches", f"{len(filtered):,}")
    c3.metric("⭐ Avg", f"{filtered['avg_rating'].mean():.2f}" if len(filtered) > 0 else "N/A")
    c4.metric("🎭 Genres", f"{g_count}")

def render_active_filters(search, genres, langs, rating, years, min_r, max_r, min_y, max_y) -> None:
    pills = []
    if search: pills.append(f"🔍 {search}")
    for g in genres: pills.append(f"🎭 {g}")
    if pills:
        p_html = "".join(f'<span class="filter-pill">{p}</span>' for p in pills)
        st.markdown(f'<div class="active-filters-row">{p_html}</div>', unsafe_allow_html=True)

def render_footer() -> None:
    st.markdown('<div style="text-align:center; padding:20px; color:#6b6b8a; font-size:12px;">Zakaria Charouite · Assignment 1</div>', unsafe_allow_html=True)
