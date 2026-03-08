from dataclasses import dataclass
import pandas as pd
import streamlit as st
from config import SORT_OPTIONS, LANGUAGE_NAMES
from utils import get_language_label

def reset_filters() -> None:
    st.session_state.filter_genres = []
    st.session_state.filter_languages = []
    st.session_state.filter_sort = "Year (Newest)"
    st.session_state.page = 1

@dataclass
class FilterState:
    search_title: str
    selected_genres: list[str]
    selected_languages: list[str]
    rating_range: tuple[float, float]
    year_range: tuple[int, int]
    sort_option: str
    min_rating: float
    max_rating: float
    min_year: int
    max_year: int

def render_sidebar_filters(df: pd.DataFrame) -> dict:
    all_genres = sorted(set(g.strip() for gs in df["genres"].dropna() for g in str(gs).split("|") if g.strip() and g != "(no genres listed)"))
    all_languages = sorted(df["language"].dropna().unique())
    min_y, max_y = 1898, 2024
    min_r, max_r = 0.0, 5.0
    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙️ Filters</div>', unsafe_allow_html=True)
        sel_genres = st.multiselect("Genres", options=all_genres, default=[], key="f_g")
        flagships = {get_language_label(c): c for c in all_languages if c in LANGUAGE_NAMES}
        opts = sorted(flagships.keys())
        if any(c not in LANGUAGE_NAMES for c in all_languages): opts.append("🌍 Others")
        sel_l_lbls = st.multiselect("Languages", options=opts, default=[], key="f_l")
        sel_langs = []
        for l in sel_l_lbls:
            if l == "🌍 Others": sel_langs.extend([c for c in all_languages if c not in LANGUAGE_NAMES])
            else: sel_langs.append(flagships[l])
        r_range = st.slider("Rating", 0.0, 5.0, (0.0, 5.0), 0.1, key="f_r")
        y_range = st.slider("Year", min_y, max_y, (min_y, max_y), 1, key="f_y")
        s_opt = st.selectbox("Sort", list(SORT_OPTIONS.keys()), index=2, key="f_s")
        st.button("🗑️ Clear", on_click=reset_filters)
    return {"selected_genres": sel_genres, "selected_languages": sel_langs, "rating_range": r_range, "year_range": y_range, "sort_option": s_opt, "min_rating": min_r, "max_rating": max_r, "min_year": min_y, "max_year": max_y}

def apply_filters(df, fs: FilterState):
    import re
    f = df.copy()
    if fs.search_title: f = f[f["title"].str.contains(re.escape(fs.search_title), case=False, na=False)]
    if fs.selected_genres: f = f[f["genres"].apply(lambda gs: any(g in [x.strip() for x in str(gs).split("|")] for g in fs.selected_genres))]
    if fs.selected_languages: f = f[f["language"].isin(fs.selected_languages)]
    f = f[(f["avg_rating"] >= fs.rating_range[0]) & (f["avg_rating"] <= fs.rating_range[1])]
    f = f[(f["release_year"] >= fs.year_range[0]) & (f["release_year"] <= fs.year_range[1])]
    sc, sa = SORT_OPTIONS[fs.sort_option]
    return f.sort_values(sc, ascending=sa).reset_index(drop=True)
