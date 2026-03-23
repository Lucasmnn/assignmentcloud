"""
MovieFlix — Netflix-style Movie Recommender
Frontend: Streamlit · Backend: Flask · Data: BigQuery + Elasticsearch + TMDB
"""

import streamlit as st
from styles import inject_css
import api_client

st.set_page_config(
    page_title="MovieFlix",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)
inject_css()

# ──────────────────────────────────────────────────────────────────
# Session state bootstrap
# ──────────────────────────────────────────────────────────────────

def _init_state() -> None:
    defaults = {
        "selected_movies": [],   # list of dicts: {movieId, title, ...}
        "recommendations":  None, # list of dicts (from backend) or None
        "show_recs":        False,
        "search_query":     "",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init_state()


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────

def _add_movie(movie: dict) -> None:
    ids = [m["movieId"] for m in st.session_state.selected_movies]
    if movie["movieId"] not in ids:
        st.session_state.selected_movies.append(movie)
        # Reset recommendations when selection changes
        st.session_state.show_recs = False
        st.session_state.recommendations = None


def _remove_movie(idx: int) -> None:
    st.session_state.selected_movies.pop(idx)
    st.session_state.show_recs = False
    st.session_state.recommendations = None


def _clear_all() -> None:
    st.session_state.selected_movies = []
    st.session_state.show_recs = False
    st.session_state.recommendations = None
    st.session_state.search_query = ""


def _genres_short(genres_str: str, max_n: int = 2) -> str:
    """Return first N genres from pipe-separated string."""
    parts = [g.strip() for g in str(genres_str).split("|") if g.strip() and g != "(no genres listed)"]
    return " · ".join(parts[:max_n])


def _year(movie: dict) -> str:
    y = int(movie.get("release_year") or 0)
    return str(y) if y > 0 else ""


def _rating_str(movie: dict) -> str:
    r = float(movie.get("avg_rating") or movie.get("predicted_rating") or 0)
    return f"{r:.1f}" if r > 0 else ""


# ──────────────────────────────────────────────────────────────────
# HTML builders
# ──────────────────────────────────────────────────────────────────

def _card_html(movie: dict, show_match: bool = False) -> str:
    title   = movie.get("title", "Unknown")
    genres  = _genres_short(movie.get("genres", ""))
    year    = _year(movie)
    rating  = _rating_str(movie)
    poster  = movie.get("poster_url")

    match_badge = ""
    if show_match and movie.get("similar_user_votes"):
        votes = int(movie["similar_user_votes"])
        match_badge = f'<div class="nf-match-badge">▶ {votes} similar users</div>'

    if poster:
        img_html = f'<img src="{poster}" alt="{title}" loading="lazy">'
    else:
        short_title = title[:30] + "…" if len(title) > 30 else title
        img_html = (
            f'<div class="nf-no-poster">'
            f'🎬<span class="nf-no-poster-title">{short_title}</span>'
            f'</div>'
        )

    meta_parts = []
    if year:
        meta_parts.append(year)
    if genres:
        meta_parts.append(genres)
    meta_str = " · ".join(meta_parts)

    rating_html = f'<div class="nf-card-rating">⭐ {rating}</div>' if rating else ""

    return f"""
    <div class="nf-card">
        {img_html}
        <div class="nf-card-overlay">
            {match_badge}
            <div class="nf-card-title">{title}</div>
            <div class="nf-card-meta">{meta_str}</div>
            {rating_html}
        </div>
    </div>
    """


def _row_html(movies: list[dict], show_match: bool = False) -> str:
    if not movies:
        return '<div class="nf-empty-state">No movies available.</div>'
    cards = "".join(_card_html(m, show_match) for m in movies)
    return f'<div class="nf-row-scroll">{cards}</div>'


def _hero_html(movie: dict) -> str:
    title    = movie.get("title", "MovieFlix")
    year     = _year(movie)
    genres   = _genres_short(movie.get("genres", ""), max_n=3)
    overview = movie.get("overview", "")[:280]
    backdrop = movie.get("backdrop_url") or ""

    bg_style = (
        f'background-image: url("{backdrop}"); background-size: cover; background-position: center 20%;'
        if backdrop else
        'background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 60%, #16213e 100%);'
    )

    meta_parts = [p for p in [year, genres] if p]
    meta_str = " · ".join(meta_parts)
    overview_html = f'<p class="nf-hero-overview">{overview}</p>' if overview else ""

    return f"""
    <div class="nf-hero" style="{bg_style}">
        <div class="nf-hero-gradient"></div>
        <div class="nf-hero-content">
            <div class="nf-hero-title">{title}</div>
            <div class="nf-hero-meta">{meta_str}</div>
            {overview_html}
        </div>
    </div>
    """


# ──────────────────────────────────────────────────────────────────
# Render sections
# ──────────────────────────────────────────────────────────────────

def render_navbar() -> None:
    st.markdown(
        '<div class="nf-navbar">'
        '  <div class="nf-logo">MovieFlix</div>'
        '  <div class="nf-nav-tagline">Personalized Recommendations · Powered by BigQuery ML</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_hero(trending: list[dict]) -> None:
    if trending:
        st.markdown(_hero_html(trending[0]), unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="nf-hero-placeholder">🎬</div>',
            unsafe_allow_html=True,
        )


def render_selector() -> None:
    """Render the movie preference selector with Elasticsearch autocomplete."""
    st.markdown(
        '<div class="nf-selector-section">'
        '  <div class="nf-selector-title">🎯 Get Personalized Recommendations</div>'
        '  <div class="nf-selector-subtitle">'
        '      Search for movies you\'ve enjoyed and we\'ll find similar ones for you.<br>'
        '      Leave empty to see our global top picks.'
        '  </div>'
        '</div>',
        unsafe_allow_html=True,
    )

    col_input, col_spacer = st.columns([3, 1])
    with col_input:
        search_q = st.text_input(
            "search",
            placeholder="🔍  Search a movie you liked… (e.g. Inception, Titanic)",
            key="search_query",
            label_visibility="collapsed",
        )

    # ── Autocomplete results ─────────────────────────────────────
    if search_q and len(search_q.strip()) >= 2:
        with st.spinner(""):
            suggestions = api_client.autocomplete(search_q)

        if suggestions:
            st.markdown(
                '<p style="color:#808080; font-size:0.82rem; margin:8px 0 4px;">Select a movie to add it:</p>',
                unsafe_allow_html=True,
            )
            cols = st.columns(min(len(suggestions), 4))
            already_selected = {m["movieId"] for m in st.session_state.selected_movies}
            for i, movie in enumerate(suggestions[:8]):
                with cols[i % 4]:
                    mid = movie["movieId"]
                    label = movie["title"]
                    yr = int(movie.get("release_year") or 0)
                    if yr:
                        label += f" ({yr})"
                    disabled = mid in already_selected
                    icon = "✓" if disabled else "＋"
                    st.markdown('<div class="ac-movie-btn">', unsafe_allow_html=True)
                    if st.button(
                        f"{icon} {label}",
                        key=f"ac_{mid}",
                        disabled=disabled,
                        use_container_width=True,
                    ):
                        _add_movie(movie)
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)
        elif search_q and len(search_q.strip()) >= 2:
            st.markdown(
                '<p style="color:#808080; font-size:0.82rem;">No matches found — try a different title.</p>',
                unsafe_allow_html=True,
            )

    # ── Selected movies chips ────────────────────────────────────
    selected = st.session_state.selected_movies
    if selected:
        st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<p style="color:#e5e5e5; font-size:0.9rem; margin-bottom:10px;">'
            f'<strong>{len(selected)}</strong> movie{"s" if len(selected) != 1 else ""} selected:'
            '</p>',
            unsafe_allow_html=True,
        )
        # Show chips as HTML display + Streamlit remove buttons
        chips_html = ""
        for m in selected:
            chips_html += f'<span class="nf-chip"><span class="nf-chip-label">{m["title"]}</span></span>'
        st.markdown(f'<div class="selected-movies-bar">{chips_html}</div>', unsafe_allow_html=True)

        # Remove buttons below chips
        rm_cols = st.columns(min(len(selected), 4))
        for i, m in enumerate(selected):
            with rm_cols[i % 4]:
                st.markdown('<div class="chip-remove">', unsafe_allow_html=True)
                if st.button(f"✕ {m['title'][:20]}", key=f"rm_{m['movieId']}_{i}"):
                    _remove_movie(i)
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    # ── Action buttons ───────────────────────────────────────────
    st.markdown('<div style="margin-top:20px; display:flex; gap:12px;">', unsafe_allow_html=True)
    col_rec, col_clear, col_pad = st.columns([2, 1, 3])
    with col_rec:
        label = "🎬 Get Recommendations" if selected else "🌟 Show Top Picks"
        st.markdown('<div class="nf-cta">', unsafe_allow_html=True)
        if st.button(label, key="btn_recommend", use_container_width=True):
            st.session_state.show_recs = True
            movie_ids = [m["movieId"] for m in st.session_state.selected_movies]
            with st.spinner("Finding your perfect movies…"):
                st.session_state.recommendations = api_client.get_recommendations(movie_ids)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    if selected:
        with col_clear:
            st.markdown('<div class="nf-clear">', unsafe_allow_html=True)
            if st.button("✕ Clear", key="btn_clear", use_container_width=True):
                _clear_all()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def render_recommendations() -> None:
    recs = st.session_state.recommendations
    if not recs:
        st.markdown(
            '<div class="nf-section"><div class="nf-empty-state">'
            'No recommendations found. Try selecting different movies.'
            '</div></div>',
            unsafe_allow_html=True,
        )
        return

    selected = st.session_state.selected_movies
    has_selection = bool(selected)

    if has_selection:
        title_text = (
            f'<span style="color:#E50914">For You</span> — '
            f'Based on your {len(selected)} selected movie{"s" if len(selected) != 1 else ""}'
        )
    else:
        title_text = '<span style="color:#E50914">Top Picks</span> — Our Global Recommendations'

    st.markdown(
        f'<div class="nf-section">'
        f'  <div class="nf-section-title">{title_text}</div>'
        + _row_html(recs, show_match=has_selection) +
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="nf-divider"></div>', unsafe_allow_html=True)


def render_movie_row(title_html: str, movies: list[dict]) -> None:
    if not movies:
        return
    st.markdown(
        f'<div class="nf-section">'
        f'  <div class="nf-section-title">{title_html}</div>'
        + _row_html(movies) +
        f'</div>',
        unsafe_allow_html=True,
    )


def render_footer() -> None:
    st.markdown(
        '<div class="nf-footer">'
        'MovieFlix &nbsp;·&nbsp; BigQuery ML &nbsp;·&nbsp; Elasticsearch &nbsp;·&nbsp; TMDB &nbsp;·&nbsp; '
        'Deployed on Google Cloud Run'
        '</div>',
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main() -> None:
    render_navbar()

    # Fetch catalog data (cached)
    with st.spinner("Loading movies…"):
        trending  = api_client.get_trending(limit=24)
        top_rated = api_client.get_top_rated(limit=24)

    # Hero banner (first trending movie)
    render_hero(trending)

    # Movie selector + autocomplete
    render_selector()

    # Recommendations row (shown after user clicks "Get Recommendations")
    if st.session_state.show_recs and st.session_state.recommendations is not None:
        render_recommendations()

    # Trending row
    render_movie_row(
        '🔥 <span style="color:#E50914">Trending</span> Now',
        trending,
    )

    # Top rated row
    render_movie_row(
        '⭐ <span style="color:#E50914">Top Rated</span> All Time',
        top_rated,
    )

    render_footer()


if __name__ == "__main__":
    main()
