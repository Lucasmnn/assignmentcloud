import math
import streamlit as st
from config import MOVIES_PER_PAGE
from styles import inject_css
from data import fetch_movies
from filters import render_sidebar_filters, apply_filters, FilterState
from components import (
    render_landing_page,
    render_main_search_bar,
    render_movie_card_html,
    show_detail_view,
    render_metrics,
    render_active_filters,
    render_footer,
)

st.set_page_config(page_title="🎬 Movie Catalog", page_icon="🎬", layout="wide", initial_sidebar_state="expanded")
inject_css()

def main() -> None:
    if "entered" not in st.session_state: st.session_state.entered = False
    if not st.session_state.entered:
        render_landing_page()
        return

    with st.spinner("🎬 Loading..."): df = fetch_movies()
    if df.empty:
        st.error("No movie data available.")
        return

    if "selected_movie" in st.session_state:
        movie_id = st.session_state.selected_movie
        movie_match = df[df["movieId"] == movie_id]
        if not movie_match.empty:
            show_detail_view(movie_match.iloc[0], df)
            return
        else: st.session_state.pop("selected_movie", None)

    s_title = render_main_search_bar(df)
    s_vals = render_sidebar_filters(df)
    fs = FilterState(search_title=s_title, **s_vals)
    filtered = apply_filters(df, fs)
    
    gc = len(sorted(set(g.strip() for gs in df["genres"].dropna() for g in str(gs).split("|") if g.strip() and g != "(no genres listed)")))
    render_metrics(df, filtered, gc)
    render_active_filters(fs.search_title, fs.selected_genres, fs.selected_languages, fs.rating_range, fs.year_range, fs.min_rating, fs.max_rating, fs.min_year, fs.max_year)

    total = len(filtered)
    pages = max(1, math.ceil(total / MOVIES_PER_PAGE))
    if "page" not in st.session_state: st.session_state.page = 1
    
    f_key = f"{fs.search_title}|{fs.selected_genres}|{fs.selected_languages}|{fs.rating_range}|{fs.year_range}|{fs.sort_option}"
    if st.session_state.get("last_filter_key") != f_key:
        st.session_state.page = 1
        st.session_state.last_filter_key = f_key

    curr_p = st.session_state.page
    if total == 0:
        st.info("No movies match your filters.")
    else:
        start = (curr_p - 1) * MOVIES_PER_PAGE
        end = min(start + MOVIES_PER_PAGE, total)
        p_movies = filtered.iloc[start:end].drop_duplicates(subset=["movieId"])
        cols = st.columns(3)
        for i, (_, m) in enumerate(p_movies.iterrows()):
            with cols[i % 3]:
                st.markdown(render_movie_card_html(m), unsafe_allow_html=True)
                if st.button(" ", key=f"c_{m['movieId']}_{i}", use_container_width=True):
                    st.session_state.selected_movie = m["movieId"]
                    st.rerun()

        p1, p2, p3 = st.columns([1, 2, 1])
        with p1:
            if curr_p > 1:
                if st.button("← Previous"): st.session_state.page -= 1; st.rerun()
        with p2: st.markdown(f'<div style="text-align:center;">Page {curr_p} of {pages}</div>', unsafe_allow_html=True)
        with p3:
            if curr_p < pages:
                if st.button("Next →"): st.session_state.page += 1; st.rerun()

    render_footer()

if __name__ == "__main__": main()
