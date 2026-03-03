import streamlit as st
import requests
import pandas as pd
import math
import os
import re
from pathlib import Path

from dotenv import load_dotenv

# Load .env from parent directory (project root)
_env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(_env_path)

# ─────────────────────────── Page Config ───────────────────────────
st.set_page_config(
    page_title="🎬 TMDB Movie Catalog",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────── TMDB API ──────────────────────────────
# Support both TMDB_API_KEY and TMDB_API_key env var names
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "") or os.environ.get("TMDB_API_key", "")
TMDB_IMG_BASE = "https://image.tmdb.org/t/p/w500"

# ─────────────────────────── Custom CSS ────────────────────────────
st.markdown("""
<style>
/* ── Import Google Font ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* ── Hide Streamlit branding ── */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0f23 0%, #1a1a3e 100%);
}
[data-testid="stSidebar"] * {
    color: #e0e0e0 !important;
}
[data-testid="stSidebar"] .stMarkdown h2 {
    color: #ffffff !important;
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 18px 22px;
    border-radius: 16px;
    color: white !important;
    box-shadow: 0 8px 32px rgba(102, 126, 234, 0.25);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
div[data-testid="stMetric"]:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(102, 126, 234, 0.35);
}
div[data-testid="stMetric"] label {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 500;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700;
}

/* ── Movie Card ── */
.movie-card {
    background: linear-gradient(145deg, #1e1e2f, #2a2a40);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
    transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
    position: relative;
    overflow: hidden;
    min-height: 200px;
    cursor: pointer;
}
.movie-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2, #f093fb);
    opacity: 0;
    transition: opacity 0.3s ease;
}
.movie-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    border-color: rgba(102, 126, 234, 0.3);
}
.movie-card:hover::before {
    opacity: 1;
}

.movie-title {
    font-size: 1.15em;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 10px;
    line-height: 1.3;
    letter-spacing: -0.01em;
}

.movie-year {
    font-size: 0.82em;
    color: #8b8ba7;
    font-weight: 500;
    margin-bottom: 12px;
}

.movie-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 14px;
    flex-wrap: wrap;
}

.movie-rating {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255, 193, 7, 0.12);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.88em;
    font-weight: 600;
    color: #ffc107;
}

.movie-lang {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(102, 126, 234, 0.12);
    padding: 5px 12px;
    border-radius: 20px;
    font-size: 0.82em;
    font-weight: 500;
    color: #667eea;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.genre-container {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 6px;
}

.genre-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.75em;
    font-weight: 600;
    letter-spacing: 0.02em;
}

/* Genre color palette */
.genre-drama { background: rgba(239, 83, 80, 0.15); color: #ef5350; }
.genre-comedy { background: rgba(255, 202, 40, 0.15); color: #ffca28; }
.genre-action { background: rgba(255, 112, 67, 0.15); color: #ff7043; }
.genre-romance { background: rgba(236, 64, 122, 0.15); color: #ec407a; }
.genre-thriller { background: rgba(171, 71, 188, 0.15); color: #ab47bc; }
.genre-horror { background: rgba(183, 28, 28, 0.15); color: #c62828; }
.genre-sci-fi { background: rgba(0, 188, 212, 0.15); color: #00bcd4; }
.genre-adventure { background: rgba(76, 175, 80, 0.15); color: #4caf50; }
.genre-animation { background: rgba(255, 167, 38, 0.15); color: #ffa726; }
.genre-musical { background: rgba(156, 39, 176, 0.15); color: #ce93d8; }
.genre-war { background: rgba(121, 85, 72, 0.15); color: #a1887f; }
.genre-crime { background: rgba(158, 158, 158, 0.15); color: #bdbdbd; }
.genre-mystery { background: rgba(63, 81, 181, 0.15); color: #7986cb; }
.genre-documentary { background: rgba(0, 150, 136, 0.15); color: #4db6ac; }
.genre-western { background: rgba(188, 143, 89, 0.15); color: #bc8f59; }
.genre-fantasy { background: rgba(126, 87, 194, 0.15); color: #7e57c2; }
.genre-children { background: rgba(129, 199, 132, 0.15); color: #81c784; }
.genre-film-noir { background: rgba(96, 96, 96, 0.18); color: #aaaaaa; }
.genre-default { background: rgba(255, 255, 255, 0.08); color: #b0b0b0; }

/* ── Star display ── */
.stars {
    color: #ffc107;
    font-size: 0.95em;
    letter-spacing: 1px;
}

/* ── Section title ── */
.section-title {
    font-size: 1.5em;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 4px;
    letter-spacing: -0.02em;
}
.section-subtitle {
    font-size: 0.95em;
    color: #8b8ba7;
    margin-bottom: 24px;
}

/* ── No results ── */
.no-results {
    text-align: center;
    padding: 60px 20px;
    color: #8b8ba7;
}
.no-results-icon {
    font-size: 4em;
    margin-bottom: 16px;
}
.no-results-text {
    font-size: 1.2em;
    font-weight: 500;
}

/* ── Pagination ── */
.pagination-info {
    text-align: center;
    color: #8b8ba7;
    font-size: 0.9em;
    padding: 10px 0;
    margin-top: 10px;
}

/* ── Divider ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent);
    margin: 24px 0;
    border: none;
}

/* ── Detail view ── */
.detail-header {
    font-size: 2em;
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    letter-spacing: -0.02em;
}
.detail-tagline {
    font-size: 1.1em;
    color: #8b8ba7;
    font-style: italic;
    margin-bottom: 20px;
}
.detail-overview {
    font-size: 1em;
    color: #c0c0d0;
    line-height: 1.7;
    margin-bottom: 20px;
}
.detail-info-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
}
.detail-info-item {
    background: #1e1e2f;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 14px 18px;
}
.detail-info-label {
    font-size: 0.78em;
    color: #8b8ba7;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    font-weight: 600;
    margin-bottom: 4px;
}
.detail-info-value {
    font-size: 1.05em;
    color: #ffffff !important;
    font-weight: 600;
}

/* ── Clickable Movie Cards Overlay ─- */
/* Target columns containing a movie card */
[data-testid="stColumn"]:has(.movie-card) {
    position: relative !important;
}

/* 
   Make the button container an absolute overlay that covers the entire card.
   We target all potential wrappers Streamlit might use for the button.
*/
[data-testid="stColumn"]:has(.movie-card) [data-testid="stElementContainer"]:has(.stButton),
[data-testid="stColumn"]:has(.movie-card) .stButton {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 10 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Ensure the button itself is invisible but covers the area */
[data-testid="stColumn"]:has(.movie-card) button {
    height: 100% !important;
    width: 100% !important;
    opacity: 0 !important;
    border: none !important;
    background: transparent !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
    cursor: pointer !important;
}

/* Ensure the visible card is below the invisible button */
.movie-card {
    position: relative;
    z-index: 1;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────── Data Fetching ─────────────────────────
API_URL = "https://fonctionsassignment1-923500071692.europe-west6.run.app"


@st.cache_data(ttl=300, show_spinner=False)
def fetch_movies():
    """Fetch movie data from the Cloud Function API with 5-minute cache."""
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, dict) and "movie_details" in data:
            data = data["movie_details"]
        df = pd.DataFrame(data)
        return df
    except requests.RequestException as e:
        st.error(f"❌ Error fetching data from API: {e}")
        return pd.DataFrame()


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_tmdb_details(title, year):
    """Search TMDB for movie details and poster by title and year."""
    if not TMDB_API_KEY:
        return None
    try:
        # Clean the title: remove year and parenthetical info for better search
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

        # Get full movie details
        detail_url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
        detail_resp = requests.get(
            detail_url, params={"api_key": TMDB_API_KEY}, timeout=10
        )
        detail_resp.raise_for_status()
        return detail_resp.json()
    except Exception:
        return None


# ─────────────────────────── Helper Functions ──────────────────────
GENRE_CSS_MAP = {
    "Drama": "drama", "Comedy": "comedy", "Action": "action",
    "Romance": "romance", "Thriller": "thriller", "Horror": "horror",
    "Sci-Fi": "sci-fi", "Adventure": "adventure", "Animation": "animation",
    "Musical": "musical", "War": "war", "Crime": "crime",
    "Mystery": "mystery", "Documentary": "documentary", "Western": "western",
    "Fantasy": "fantasy", "Children": "children", "Film-Noir": "film-noir",
}

LANGUAGE_NAMES = {
    "en": "🇬🇧 English", "fr": "🇫🇷 French", "de": "🇩🇪 German",
    "it": "🇮🇹 Italian", "ja": "🇯🇵 Japanese", "es": "🇪🇸 Spanish",
    "ru": "🇷🇺 Russian", "sv": "🇸🇪 Swedish", "zh": "🇨🇳 Chinese",
    "da": "🇩🇰 Danish", "fi": "🇫🇮 Finnish", "ko": "🇰🇷 Korean",
    "no": "🇳🇴 Norwegian", "pl": "🇵🇱 Polish", "id": "🇮🇩 Indonesian",
    "xx": "🌍 Unknown",
}


def get_language_label(code):
    return LANGUAGE_NAMES.get(code, f"🌍 {code.upper()}")


def render_stars(rating):
    full = int(rating)
    half = 1 if (rating - full) >= 0.4 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


def get_genre_class(genre):
    return f"genre-{GENRE_CSS_MAP.get(genre, 'default')}"


def render_movie_card_html(movie):
    """Render movie card HTML content (used inside a clickable button)."""
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


# ─────────────────────────── Detail View ───────────────────────────
def show_detail_view(movie_row, df):
    """Display detailed movie view with TMDB poster and info."""

    # Back button
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

    # Fetch TMDB details
    with st.spinner("🎬 Loading movie details from TMDB..."):
        tmdb = fetch_tmdb_details(title, year)

    col_poster, col_info = st.columns([1, 2])

    with col_poster:
        if tmdb and tmdb.get("poster_path"):
            poster_url = f"{TMDB_IMG_BASE}{tmdb['poster_path']}"
            st.image(poster_url, use_container_width=True)
        else:
            # Placeholder when no poster
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

    with col_info:
        # Title
        st.markdown(f'<div class="detail-header">{title}</div>', unsafe_allow_html=True)

        # Tagline from TMDB
        if tmdb and tmdb.get("tagline"):
            st.markdown(
                f'<div class="detail-tagline">"{tmdb["tagline"]}"</div>',
                unsafe_allow_html=True,
            )

        # Genre badges
        genre_badges = "".join(
            f'<span class="genre-badge {get_genre_class(g)}">{g}</span>'
            for g in genres
        )
        st.markdown(
            f'<div class="genre-container" style="margin-bottom:20px">{genre_badges}</div>',
            unsafe_allow_html=True,
        )

        # Info grid
        info_items = [
            ("📅 Release Year", year),
            ("🌐 Language", get_language_label(lang_code)),
            ("⭐ Catalog Rating", f"{render_stars(rating)} {rating:.2f}/5")
        ]
        
        if tmdb:
            if tmdb.get("vote_average"):
                info_items.append(("🎬 TMDB Rating", f"{tmdb['vote_average']:.1f}/10 ({tmdb['vote_count']:,} votes)"))
            if tmdb.get("runtime"):
                info_items.append(("⏱️ Runtime", f"{tmdb['runtime']} min"))
            if tmdb.get("budget"):
                info_items.append(("💰 Budget", f"${tmdb['budget']:,.0f}"))
            if tmdb.get("revenue"):
                info_items.append(("📈 Revenue", f"${tmdb['revenue']:,.0f}"))
        
        info_items.append(("� Movie ID", int(movie_row["movieId"])))

        grid_html = '<div class="detail-info-grid">'
        for label, value in info_items:
            grid_html += f'<div class="detail-info-item"><div class="detail-info-label">{label}</div><div class="detail-info-value" style="color: white !important;">{value}</div></div>'
        grid_html += '</div>'
        
        st.markdown(grid_html, unsafe_allow_html=True)

        # Overview
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


# ─────────────────────────── Main App ──────────────────────────────
def main():
    # Load data
    with st.spinner("🎬 Loading movie catalog..."):
        df = fetch_movies()

    if df.empty:
        st.error("No movie data available. Please check the API connection.")
        return

    # ────────── Detail View Mode ──────────
    if "selected_movie" in st.session_state:
        movie_id = st.session_state.selected_movie
        movie_match = df[df["movieId"] == movie_id]
        if not movie_match.empty:
            show_detail_view(movie_match.iloc[0], df)
            return
        else:
            st.session_state.pop("selected_movie", None)

    # Prepare data
    all_titles = sorted(df["title"].dropna().unique().tolist())
    all_genres = sorted(set(
        g.strip()
        for genres_str in df["genres"].dropna()
        for g in str(genres_str).split("|")
        if g.strip() and g.strip() != "(no genres listed)"
    ))
    all_languages = sorted(df["language"].dropna().unique())
    min_year = int(df["release_year"].min())
    max_year = int(df["release_year"].max())
    min_rating = float(df["avg_rating"].min())
    max_rating = float(df["avg_rating"].max())

    # ────────── Sidebar Filters ──────────
    with st.sidebar:
        st.markdown("## 🎬 Movie Catalog")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Title search with autocomplete
        st.markdown("#### 🔍 Search by Title")
        search_title = st.selectbox(
            "Type to search...",
            options=[""] + all_titles,
            index=0,
            placeholder="Start typing a movie title...",
            label_visibility="collapsed",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Genre filter
        st.markdown("#### 🎭 Genre")
        selected_genres = st.multiselect(
            "Select genres",
            options=all_genres,
            default=[],
            label_visibility="collapsed",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Language filter
        st.markdown("#### 🌐 Language")
        language_options = {get_language_label(code): code for code in all_languages}
        selected_lang_labels = st.multiselect(
            "Select languages",
            options=sorted(language_options.keys()),
            default=[],
            label_visibility="collapsed",
        )
        selected_languages = [language_options[label] for label in selected_lang_labels]

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Rating filter
        st.markdown("#### ⭐ Average Rating")
        rating_range = st.slider(
            "Rating range",
            min_value=round(min_rating, 1),
            max_value=round(max_rating, 1),
            value=(round(min_rating, 1), round(max_rating, 1)),
            step=0.1,
            label_visibility="collapsed",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Year filter
        st.markdown("#### 📅 Release Year")
        year_range = st.slider(
            "Year range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            label_visibility="collapsed",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        # Sort
        st.markdown("#### 📊 Sort by")
        sort_option = st.selectbox(
            "Sort option",
            ["Rating (High → Low)", "Rating (Low → High)",
             "Year (Newest)", "Year (Oldest)", "Title (A → Z)"],
            label_visibility="collapsed",
        )

    # ────────── Apply Filters ──────────
    filtered = df.copy()

    # Title filter (exact match from selectbox)
    if search_title:
        filtered = filtered[
            filtered["title"].str.contains(
                re.escape(search_title), case=False, na=False
            )
        ]

    # Genre filter
    if selected_genres:
        def has_genre(genres_str):
            movie_genres = [g.strip() for g in str(genres_str).split("|")]
            return any(g in movie_genres for g in selected_genres)
        filtered = filtered[filtered["genres"].apply(has_genre)]

    # Language filter
    if selected_languages:
        filtered = filtered[filtered["language"].isin(selected_languages)]

    # Rating filter
    filtered = filtered[
        (filtered["avg_rating"] >= rating_range[0])
        & (filtered["avg_rating"] <= rating_range[1])
    ]

    # Year filter
    filtered = filtered[
        (filtered["release_year"] >= year_range[0])
        & (filtered["release_year"] <= year_range[1])
    ]

    # ────────── Sort ──────────
    sort_map = {
        "Rating (High → Low)": ("avg_rating", False),
        "Rating (Low → High)": ("avg_rating", True),
        "Year (Newest)": ("release_year", False),
        "Year (Oldest)": ("release_year", True),
        "Title (A → Z)": ("title", True),
    }
    sort_col, sort_asc = sort_map[sort_option]
    filtered = filtered.sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)

    # ────────── Header & Metrics ──────────
    st.markdown(
        '<div class="section-title">🎬 TMDB Movie Catalog</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="section-subtitle">'
        "Explore, filter, and discover movies from the TMDB dataset"
        "</div>",
        unsafe_allow_html=True,
    )

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🎞️ Total Movies", f"{len(df):,}")
    col2.metric("🔎 Matching", f"{len(filtered):,}")
    col3.metric(
        "⭐ Avg Rating",
        f"{filtered['avg_rating'].mean():.2f}" if len(filtered) > 0 else "—",
    )
    col4.metric("🎭 Genres", f"{len(all_genres)}")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

    # ────────── Pagination ──────────
    MOVIES_PER_PAGE = 24
    total_movies = len(filtered)
    total_pages = max(1, math.ceil(total_movies / MOVIES_PER_PAGE))

    if "page" not in st.session_state:
        st.session_state.page = 1

    # Reset page when filters change
    filter_key = f"{search_title}|{selected_genres}|{selected_languages}|{rating_range}|{year_range}|{sort_option}"
    if st.session_state.get("last_filter_key") != filter_key:
        st.session_state.page = 1
        st.session_state.last_filter_key = filter_key

    current_page = st.session_state.page

    # ────────── Display Movies ──────────
    if total_movies == 0:
        st.markdown(
            """
            <div class="no-results">
                <div class="no-results-icon">🔍</div>
                <div class="no-results-text">No movies match your filters</div>
                <p style="color:#6b6b8a; margin-top:8px;">
                    Try adjusting your search criteria
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        start_idx = (current_page - 1) * MOVIES_PER_PAGE
        end_idx = min(start_idx + MOVIES_PER_PAGE, total_movies)
        page_movies = filtered.iloc[start_idx:end_idx]

        # Render 3-column grid — entire card is clickable
        cols = st.columns(3)
        for idx, (_, movie) in enumerate(page_movies.iterrows()):
            with cols[idx % 3]:
                # Render the visual card
                st.markdown(render_movie_card_html(movie), unsafe_allow_html=True)
                
                # Overlay an invisible button
                if st.button(" ", key=f"card_{movie['movieId']}", use_container_width=True):
                    st.session_state.selected_movie = movie["movieId"]
                    st.rerun()

        # Pagination controls
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="pagination-info">Showing {start_idx + 1}–{end_idx} of {total_movies} movies</div>',
            unsafe_allow_html=True,
        )

        pcol1, pcol2, pcol3 = st.columns([1, 2, 1])
        with pcol1:
            if current_page > 1:
                if st.button("← Previous", use_container_width=True):
                    st.session_state.page -= 1
                    st.rerun()
        with pcol2:
            st.markdown(
                f'<div style="text-align:center; padding:8px; color:#8b8ba7;">'
                f"Page {current_page} of {total_pages}</div>",
                unsafe_allow_html=True,
            )
        with pcol3:
            if current_page < total_pages:
                if st.button("Next →", use_container_width=True):
                    st.session_state.page += 1
                    st.rerun()


if __name__ == "__main__":
    main()
