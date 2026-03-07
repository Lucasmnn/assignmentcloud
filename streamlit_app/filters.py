from dataclasses import dataclass

import pandas as pd
import streamlit as st

from config import SORT_OPTIONS
from utils import get_language_label




def reset_filters() -> None:
    """Callback to clear all filter-related session state keys."""
    st.session_state.filter_title = ""
    st.session_state.filter_genres = []
    st.session_state.filter_languages = []
    st.session_state.filter_sort = "Year (Newest)"

    for k in ["filter_rating", "filter_year", "selected_movie"]:
        if k in st.session_state:
            del st.session_state[k]

    st.session_state.page = 1


@dataclass
class FilterState:
    """Container holding the current values of all sidebar filters."""
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
    """Render filter widgets inside the Streamlit sidebar (compact layout)."""
    all_genres = sorted(set(
        g.strip()
        for genres_str in df["genres"].dropna()
        for g in str(genres_str).split("|")
        if g.strip() and g.strip() != "(no genres listed)"
    ))
    all_languages = sorted(df["language"].dropna().unique())
    all_titles = sorted(df["title"].dropna().unique().tolist())

    valid_years = df["release_year"].dropna().astype(int)
    min_year = int(valid_years.min()) if not valid_years.empty else 1900
    max_year = int(valid_years.max()) if not valid_years.empty else 2024

    min_rating = float(df["avg_rating"].min())
    max_rating = float(df["avg_rating"].max())

    with st.sidebar:
        st.markdown("## 🎬 Movie Catalog")
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("#### 🔍 Search by Title")
        search_title = st.selectbox(
            "Type to search...",
            options=[""] + all_titles,
            index=0,
            placeholder="Start typing a movie title...",
            label_visibility="collapsed",
            key="filter_title",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("#### 🎭 Genre")
        selected_genres = st.multiselect(
            "Select genres",
            options=all_genres,
            default=[],
            label_visibility="collapsed",
            key="filter_genres",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("#### 🌐 Language")
        language_options = {get_language_label(code): code for code in all_languages}
        selected_lang_labels = st.multiselect(
            "Select languages",
            options=sorted(language_options.keys()),
            default=[],
            label_visibility="collapsed",
            key="filter_languages",
        )
        selected_languages = [language_options[lbl] for lbl in selected_lang_labels]

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("#### ⭐ Average Rating")
        rating_range = st.slider(
            "Rating range",
            min_value=round(min_rating, 1),
            max_value=round(max_rating, 1),
            value=(round(min_rating, 1), round(max_rating, 1)),
            step=0.1,
            label_visibility="collapsed",
            key="filter_rating",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("#### 📅 Release Year")
        year_range = st.slider(
            "Year range",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            label_visibility="collapsed",
            key="filter_year",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

        st.markdown("#### 📊 Sort by")
        sort_option = st.selectbox(
            "Sort option",
            list(SORT_OPTIONS.keys()),
            label_visibility="collapsed",
            key="filter_sort",
        )

        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        st.button(
            "🗑️ Clear All Filters",
            on_click=reset_filters,
            use_container_width=True,
            key="clear_filters"
        )

    return {
        "search_title": search_title,
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


def apply_filters(df: pd.DataFrame, fs: FilterState) -> pd.DataFrame:
    """Apply all active filters and sort the movie DataFrame.

    Args:
        df: Full movie DataFrame.
        fs: Current :class:`FilterState` from the sidebar.

    Returns:
        A filtered and sorted copy of *df*.
    """
    import re

    filtered = df.copy()

    if fs.search_title:
        filtered = filtered[
            filtered["title"].str.contains(
                re.escape(fs.search_title), case=False, na=False
            )
        ]

    if fs.selected_genres:
        def _has_genre(genres_str: str) -> bool:
            movie_genres = [g.strip() for g in str(genres_str).split("|")]
            return any(g in movie_genres for g in fs.selected_genres)
        filtered = filtered[filtered["genres"].apply(_has_genre)]

    if fs.selected_languages:
        filtered = filtered[filtered["language"].isin(fs.selected_languages)]

    filtered = filtered[
        (filtered["avg_rating"] >= fs.rating_range[0])
        & (filtered["avg_rating"] <= fs.rating_range[1])
    ]

    filtered = filtered[
        (filtered["release_year"] >= fs.year_range[0])
        & (filtered["release_year"] <= fs.year_range[1])
    ]

    sort_col, sort_asc = SORT_OPTIONS[fs.sort_option]
    filtered = filtered.sort_values(sort_col, ascending=sort_asc).reset_index(drop=True)

    return filtered
