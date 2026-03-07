from dataclasses import dataclass

import pandas as pd
import streamlit as st

from config import SORT_OPTIONS
from utils import get_language_label




def reset_filters() -> None:
    """Callback to clear all filter-related session state keys."""
    # Explicitly set defaults for UI sync
    st.session_state.filter_title = ""
    st.session_state.filter_genres = []
    st.session_state.filter_languages = []
    st.session_state.filter_sort = "Rating (High → Low)"
    
    # Sliders and specific states can be deleted to revert to widget defaults
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



def render_sidebar_filters(df: pd.DataFrame) -> tuple[dict, list[str]]:
    """Render filter widgets inside the Streamlit sidebar (compact layout).

    This function no longer renders the Title search bar. It returns
    the list of all titles so the main page can render it.

    Args:
        df: The full (unfiltered) movie DataFrame.

    Returns:
        A tuple of (sidebar_values_dict, all_titles).
    """
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
    all_titles = sorted(df["title"].dropna().unique().tolist())

    with st.sidebar:
        st.markdown("## 🎬 Filters")

        selected_genres = st.multiselect(
            "🎭 Genre",
            options=all_genres,
            default=[],
            key="filter_genres",
        )

        language_options = {get_language_label(code): code for code in all_languages}
        selected_lang_labels = st.multiselect(
            "🌐 Language",
            options=sorted(language_options.keys()),
            default=[],
            key="filter_languages",
        )
        selected_languages = [language_options[lbl] for lbl in selected_lang_labels]

        rating_range = st.slider(
            "⭐ Rating",
            min_value=round(min_rating, 1),
            max_value=round(max_rating, 1),
            value=(round(min_rating, 1), round(max_rating, 1)),
            step=0.1,
            key="filter_rating",
        )

        year_range = st.slider(
            "📅 Year",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="filter_year",
        )

        sort_option = st.selectbox(
            "📊 Sort by",
            list(SORT_OPTIONS.keys()),
            key="filter_sort",
        )

        st.markdown("")
        st.markdown('<div class="clear-filters-btn">', unsafe_allow_html=True)
        st.button(
            "🗑️ Clear All Filters",
            on_click=reset_filters,
            use_container_width=True,
            key="clear_filters"
        )
        st.markdown("</div>", unsafe_allow_html=True)

    sidebar_vals = {
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

    return sidebar_vals, all_titles


def render_search_bar(all_titles: list[str]) -> str:
    """Render the title search bar on the main page.

    Args:
        all_titles: Sorted list of all movie titles.

    Returns:
        The currently selected title string (empty if none).
    """
    return st.selectbox(
        "🔍 Search by Title",
        options=[""] + all_titles,
        index=0,
        placeholder="Start typing a movie title...",
        label_visibility="collapsed",
        key="filter_title",
    )


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
