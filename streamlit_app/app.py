import math

import streamlit as st

from config import MOVIES_PER_PAGE
from styles import inject_css
from data import fetch_movies
from filters import render_sidebar_filters, apply_filters
from components import (
    render_movie_card_html,
    show_detail_view,
    render_metrics,
    render_active_filters,
    render_footer,
)

st.set_page_config(
    page_title="🎬 Movie Catalog",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_css()



def main() -> None:
    """Application entry point."""

    with st.spinner("🎬 Loading movie catalog..."):
        df = fetch_movies()

    if df.empty:
        st.error("No movie data available. Please check the API connection.")
        return

    if "selected_movie" in st.session_state:
        movie_id = st.session_state.selected_movie
        movie_match = df[df["movieId"] == movie_id]
        if not movie_match.empty:
            show_detail_view(movie_match.iloc[0], df)
            return
        else:
            st.session_state.pop("selected_movie", None)

    st.markdown(
        '<div class="section-title">🎬 Movie Catalog</div>',
        unsafe_allow_html=True,
    )

    all_genres = sorted(set(
        g.strip()
        for genres_str in df["genres"].dropna()
        for g in str(genres_str).split("|")
        if g.strip() and g.strip() != "(no genres listed)"
    ))

    from filters import render_sidebar_filters, render_search_bar, FilterState
    sidebar_vals, all_titles = render_sidebar_filters(df)

    search_title = st.session_state.get("filter_title", "")

    fs = FilterState(search_title=search_title, **sidebar_vals)
    filtered = apply_filters(df, fs)

    render_metrics(df, filtered, all_genres)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    st.markdown("#### 🔍 Search by Title")
    new_search_title = render_search_bar(all_titles)
    
    if new_search_title != search_title:
        st.session_state.filter_title = new_search_title
        st.rerun()

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    render_active_filters(
        search_title=fs.search_title,
        selected_genres=fs.selected_genres,
        selected_languages=fs.selected_languages,
        rating_range=fs.rating_range,
        year_range=fs.year_range,
        min_rating=fs.min_rating,
        max_rating=fs.max_rating,
        min_year=fs.min_year,
        max_year=fs.max_year,
    )


    total_movies = len(filtered)
    total_pages = max(1, math.ceil(total_movies / MOVIES_PER_PAGE))

    if "page" not in st.session_state:
        st.session_state.page = 1

    filter_key = (
        f"{fs.search_title}|{fs.selected_genres}|{fs.selected_languages}"
        f"|{fs.rating_range}|{fs.year_range}|{fs.sort_option}"
    )
    if st.session_state.get("last_filter_key") != filter_key:
        st.session_state.page = 1
        st.session_state.last_filter_key = filter_key

    current_page = st.session_state.page

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
        # Final safety deduplication to prevent key collisions
        page_movies = page_movies.drop_duplicates(subset=["movieId"])

        cols = st.columns(3)
        for idx, (_, movie) in enumerate(page_movies.iterrows()):
            with cols[idx % 3]:
                st.markdown(render_movie_card_html(movie), unsafe_allow_html=True)
                # Use a combined key of ID and index for absolute uniqueness
                m_id = movie["movieId"]
                if st.button(" ", key=f"card_{m_id}_{idx}", use_container_width=True):
                    st.session_state.selected_movie = m_id
                    st.rerun()

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

    render_footer()


if __name__ == "__main__":
    main()
