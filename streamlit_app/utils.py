from config import LANGUAGE_NAMES, GENRE_CSS_MAP


def get_language_label(code: str) -> str:
    """Return a human-readable label (with flag emoji) for a language code.

    Args:
        code: ISO 639-1 language code (e.g. ``"en"``, ``"fr"``).

    Returns:
        Formatted string like ``"🇬🇧 English"`` or ``"🌍 XX"`` for unknown codes.
    """
    return LANGUAGE_NAMES.get(code, f"🌍 {code.upper()}")


def render_stars(rating: float) -> str:
    """Convert a numeric rating (0–5) into a star string.

    Args:
        rating: Movie rating on a 0-5 scale.

    Returns:
        A string such as ``"★★★½☆"`` representing the rating visually.
    """
    full = int(rating)
    half = 1 if (rating - full) >= 0.4 else 0
    empty = 5 - full - half
    return "★" * full + ("½" if half else "") + "☆" * empty


def get_genre_class(genre: str) -> str:
    """Map a genre name to its CSS class suffix.

    Args:
        genre: Genre name such as ``"Drama"`` or ``"Sci-Fi"``.

    Returns:
        CSS class like ``"genre-drama"`` or ``"genre-default"`` if unrecognized.
    """
    return f"genre-{GENRE_CSS_MAP.get(genre, 'default')}"
