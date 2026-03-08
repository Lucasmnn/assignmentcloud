from dataclasses import dataclass
import pandas as pd
import streamlit as st
from config import SORT_OPTIONS, LANGUAGE_NAMES
from utils import get_language_label

def reset_filters() -> None:
    """Callback to clear all filter-related session state keys."""
    st.session_state.filter_title = ""
    st.session_state.filter_genres = []
    st.session_state.filter_languages = []
    st.session_state.filter_sort = "Year (Newest)"

    if "filter_rating" in st.session_state:
        del st.session_state.filter_rating
    if "filter_year" in st.session_state:
        del st.session_state.filter_year
    if "selected_movie" in st.session_state:
        del st.session_state.selected_movie

    st.session_state.page = 1


@dataclass
class FilterState:
    """Container holding current filter values."""
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
    """Render compact filter widgets inside the Streamlit sidebar."""
    all_genres = sorted(set(
        g.strip()
        for genres_str in df["genres"].dropna()
        for g in str(genres_str).split("|")
        if g.strip() and g.strip() != "(no genres listed)"
    ))
    all_languages = sorted(df["language"].dropna().unique())
    
    valid_years = df["release_year"].dropna().astype(int)
    min_year = int(valid_years.min()) if not valid_years.empty else 1898
    max_year = int(valid_years.max()) if not valid_years.empty else 2024
    
    min_rating = float(df["avg_rating"].min())
    max_rating = float(df["avg_rating"].max())

    with st.sidebar:
        st.markdown('<div class="sidebar-title">⚙️ Filters</div>', unsafe_allow_html=True)
        
        # Genre filter
        st.markdown("#### 🎭 Genre")
        selected_genres = st.multiselect(
            "Select genres", options=all_genres, default=[], label_visibility="collapsed", key="filter_genres"
        )

        # Language filter
        st.markdown("#### 🌐 Language")
        flagships = {get_language_label(code): code for code in all_languages if code in LANGUAGE_NAMES}
        has_others = any(code not in LANGUAGE_NAMES for code in all_languages)
        options = sorted(flagships.keys())
        if has_others: options.append("🌍 Others")
            
        selected_lang_labels = st.multiselect(
            "Select languages", options=options, default=[], label_visibility="collapsed", key="filter_languages"
        )
        
        selected_languages = []
        for lbl in selected_lang_labels:
            if lbl == "🌍 Others":
                selected_languages.extend([code for code in all_languages if code not in LANGUAGE_NAMES])
            else:
                selected_languages.append(flagships[lbl])

        # Rating filter
        st.markdown("#### ⭐ Rating")
        rating_range = st.slider(
            "Rating range",
            min_value=round(min_rating, 1),
            max_value=round(max_rating, 1),
            value=(round(min_rating, 1), round(max_rating, 1)),
            step=0.1, label_visibility="collapsed", key="filter_rating"
        )

        # Year filter
        st.markdown("#### 📅 Year")
        year_range = st.slider(
            "Year range",
            min_value=min_year, max_value=max_year,
            value=(min_year, max_year),
            label_visibility="collapsed", key="filter_year"
        )

        # Sort
        st.markdown("#### 📊 Sort")
        sort_option = st.selectbox(
            "Sort option", list(SORT_OPTIONS.keys()), index=2, label_visibility="collapsed", key="filter_sort"
        )

        st.markdown('<div style="margin-top:20px"></div>', unsafe_allow_html=True)
        st.button("🗑️ Clear All", on_click=reset_filters, use_container_width=True)

    return {
        "selected_genres": selected_genres,
        "selected_languages": selected_languages,
        "rating_range": rating_range,
        "year_range": year_range,
        "sort_option": sort_option,
        "min_rating": round(min_rating, 1),
        "max_rating": round(max_rating, 1),
        "min_year": min_year,
        "max_year": max_year,
    }


def apply_filters(df, fs: FilterState):
    """Filter and sort the movie collection based on state."""
    import re
    filtered = df.copy()

    if fs.search_title:
        filtered = filtered[filtered["title"].str.contains(re.escape(fs.search_title), case=False, na=False)]

    if fs.selected_genres:
        def _has_genre(gs):
            m_gs = [g.strip() for g in str(gs).split("|")]
            return any(g in m_gs for g in fs.selected_genres)
        filtered = filtered[filtered["genres"].apply(_has_genre)]

    if fs.selected_languages:
        filtered = filtered[filtered["language"].isin(fs.selected_languages)]

    filtered = filtered[
        (filtered["avg_rating"] >= fs.rating_range[0]) & 
        (filtered["avg_rating"] <= fs.rating_range[1])
    ]

    filtered = filtered[
        (filtered["release_year"] >= fs.year_range[0]) & 
        (filtered["release_year"] <= fs.year_range[1])
    ]

    s_col, s_asc = SORT_OPTIONS[fs.sort_option]
    return filtered.sort_values(s_col, ascending=s_asc).reset_index(drop=True)
