from typing import Optional

import pandas as pd
import streamlit as st

from config import TMDB_API_KEY, TMDB_IMG_BASE, TMDB_IMG_SMALL
from data import fetch_tmdb_details
from utils import get_genre_class, get_language_label, render_stars



def render_movie_card_html(movie: pd.Series) -> str:
   
    genres = str(movie.get("genres", "")).split("|")
    genres = [g.strip() for g in genres if g.strip() and g != "(no genres listed)"]

    genre_badges = "".join(
        f'<span class="genre-badge {get_genre_class(g)}">{g}</span>'
        for g in genres
    )

    rating = movie.get("avg_rating", 0)
    stars = render_stars(rating)
    lang_code = movie.get("language", "xx")

    return f"""
    <div class="movie-card">
        <div class="movie-title">{movie.get("title", "Unknown")}</div>
        <div class="movie-year">📅 {int(movie.get("release_year", 0))}</div>
        <div class="movie-meta">
            <span class="movie-rating">
                <span class="stars">{stars}</span>
                {rating:.1f}/5
            </span>
            <span class="movie-lang">🌐 {get_language_label(lang_code)}</span>
        </div>
        <div class="genre-container">{genre_badges}</div>
    </div>
    """



def show_detail_view(movie_row: pd.Series, df: pd.DataFrame) -> None:
 
    if st.button("← Back to Catalog", use_container_width=False):
        st.session_state.pop("selected_movie", None)
        st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    title = movie_row["title"]
    year = int(movie_row["release_year"])
    rating = movie_row["avg_rating"]
    lang_code = movie_row.get("language", "xx")
    genres = str(movie_row.get("genres", "")).split("|")
    genres = [g.strip() for g in genres if g.strip() and g != "(no genres listed)"]

    with st.spinner("🎬 Loading movie details from TMDB..."):
        tmdb = fetch_tmdb_details(title, year)

    col_poster, col_info = st.columns([1, 2])

    with col_poster:
        if tmdb and tmdb.get("poster_path"):
            poster_url = f"{TMDB_IMG_BASE}{tmdb['poster_path']}"
            st.image(poster_url, use_container_width=True)
        else:
            _render_poster_placeholder()

    with col_info:
        _render_detail_info(title, year, rating, lang_code, genres, tmdb, movie_row)


def _render_poster_placeholder() -> None:
    """Show a placeholder when no TMDB poster is available."""
    st.markdown(
        """
        <div style="
            background: linear-gradient(145deg, #1e1e2f, #2a2a40);
            border-radius: 16px;
            height: 450px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 4em;
            color: #3a3a5c;
        ">🎬</div>
        """,
        unsafe_allow_html=True,
    )
    if not TMDB_API_KEY:
        st.warning("⚠️ TMDB API key not found. Add `TMDB_API_KEY=...` to your `.env`.")


def _render_detail_info(
    title: str,
    year: int,
    rating: float,
    lang_code: str,
    genres: list[str],
    tmdb: Optional[dict],
    movie_row: pd.Series,
) -> None:
    """Render the right-hand info column of the detail view."""
    st.markdown(f'<div class="detail-header">{title}</div>', unsafe_allow_html=True)

    if tmdb and tmdb.get("tagline"):
        st.markdown(
            f'<div class="detail-tagline">"{tmdb["tagline"]}"</div>',
            unsafe_allow_html=True,
        )

    genre_badges = "".join(
        f'<span class="genre-badge {get_genre_class(g)}">{g}</span>' for g in genres
    )
    st.markdown(
        f'<div class="genre-container" style="margin-bottom:20px">{genre_badges}</div>',
        unsafe_allow_html=True,
    )

    info_items: list[tuple[str, object]] = [
        ("📅 Release Year", year),
        ("🌐 Language", get_language_label(lang_code)),
        ("⭐ Catalog Rating", f"{render_stars(rating)} {rating:.2f}/5"),
    ]

    if tmdb:
        if tmdb.get("vote_average"):
            info_items.append(
                ("🎬 TMDB Rating", f"{tmdb['vote_average']:.1f}/10 ({tmdb['vote_count']:,} votes)")
            )
        if tmdb.get("runtime"):
            info_items.append(("⏱️ Runtime", f"{tmdb['runtime']} min"))
        if tmdb.get("budget"):
            info_items.append(("💰 Budget", f"${tmdb['budget']:,.0f}"))
        if tmdb.get("revenue"):
            info_items.append(("📈 Revenue", f"${tmdb['revenue']:,.0f}"))

    info_items.append(("✦ Movie ID", int(movie_row["movieId"])))

    grid_html = '<div class="detail-info-grid">'
    for label, value in info_items:
        grid_html += (
            f'<div class="detail-info-item">'
            f'<div class="detail-info-label">{label}</div>'
            f'<div class="detail-info-value" style="color: white !important;">{value}</div>'
            f'</div>'
        )
    grid_html += "</div>"
    st.markdown(grid_html, unsafe_allow_html=True)

    if tmdb and tmdb.get("overview"):
        st.markdown("#### 📖 Synopsis")
        st.markdown(
            f'<div class="detail-overview">{tmdb["overview"]}</div>',
            unsafe_allow_html=True,
        )

    # Production companies
    if tmdb and tmdb.get("production_companies"):
        companies = ", ".join(c["name"] for c in tmdb["production_companies"][:5])
        st.markdown(
            f"""
            <div class="detail-info-item" style="margin-top:8px">
                <div class="detail-info-label">🏢 Production</div>
                <div class="detail-info-value" style="font-size:0.92em">{companies}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )



def render_metrics(df: pd.DataFrame, filtered: pd.DataFrame, all_genres: list[str]) -> None:
    """Render the top metrics row (total movies, matching, avg rating, genres).

    Args:
        df: Full (unfiltered) movie DataFrame.
        filtered: Currently filtered DataFrame.
        all_genres: List of all unique genres in the dataset.
    """
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎞️ Total Movies", f"{len(df):,}")
    col2.metric("🔎 Matching", f"{len(filtered):,}")
    col3.metric(
        "⭐ Avg Rating",
        f"{filtered['avg_rating'].mean():.2f}" if len(filtered) > 0 else "—",
    )
    col4.metric("🎭 Genres", f"{len(all_genres)}")


def render_active_filters(
    search_title: str,
    selected_genres: list[str],
    selected_languages: list[str],
    rating_range: tuple[float, float],
    year_range: tuple[int, int],
    min_rating: float,
    max_rating: float,
    min_year: int,
    max_year: int,
) -> None:
    """Display active filter pills above the movie grid.

    Only shows pills for filters that differ from their default values.
    """
    pills: list[str] = []

    if search_title:
        pills.append(f'🔍 "{search_title}"')
    for g in selected_genres:
        pills.append(f"🎭 {g}")
    for lang in selected_languages:
        pills.append(f"🌐 {lang}")
    if rating_range != (round(min_rating, 1), round(max_rating, 1)):
        pills.append(f"⭐ {rating_range[0]}–{rating_range[1]}")
    if year_range != (min_year, max_year):
        pills.append(f"📅 {year_range[0]}–{year_range[1]}")

    if pills:
        pills_html = "".join(f'<span class="filter-pill">{p}</span>' for p in pills)
        st.markdown(
            f'<div class="active-filters-bar">{pills_html}</div>',
            unsafe_allow_html=True,
        )



def render_footer() -> None:
    """Render the application footer with attribution."""
    st.markdown(
        '<div class="app-footer">'
        "Built with Streamlit · Data from TMDB · Deployed on Google Cloud Run"
        "</div>",
        unsafe_allow_html=True,
    )
