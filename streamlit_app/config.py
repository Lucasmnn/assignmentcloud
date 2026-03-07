import os
from pathlib import Path
from dotenv import load_dotenv

_app_dir = Path(__file__).resolve().parent
load_dotenv(_app_dir / ".env")
load_dotenv(_app_dir.parent / ".env")


TMDB_API_KEY: str = os.environ.get("TMDB_API_KEY", "") or os.environ.get("TMDB_API_key", "")
TMDB_IMG_BASE: str = "https://image.tmdb.org/t/p/w500"
TMDB_IMG_SMALL: str = "https://image.tmdb.org/t/p/w200"

API_URL: str = os.environ.get(
    "API_URL", "https://fonctionsassignment1-923500071692.europe-west6.run.app"
)


MOVIES_PER_PAGE: int = 24
CACHE_TTL_MOVIES: int = 300       
CACHE_TTL_TMDB: int = 3600        


GENRE_CSS_MAP: dict[str, str] = {
    "Drama": "drama", "Comedy": "comedy", "Action": "action",
    "Romance": "romance", "Thriller": "thriller", "Horror": "horror",
    "Sci-Fi": "sci-fi", "Adventure": "adventure", "Animation": "animation",
    "Musical": "musical", "War": "war", "Crime": "crime",
    "Mystery": "mystery", "Documentary": "documentary", "Western": "western",
    "Fantasy": "fantasy", "Children": "children", "Film-Noir": "film-noir",
}

LANGUAGE_NAMES: dict[str, str] = {
    "en": "🇬🇧 English", "fr": "🇫🇷 French", "de": "🇩🇪 German",
    "it": "🇮🇹 Italian", "ja": "🇯🇵 Japanese", "es": "🇪🇸 Spanish",
    "ru": "🇷🇺 Russian", "sv": "🇸🇪 Swedish", "zh": "🇨🇳 Chinese",
    "da": "🇩🇰 Danish", "fi": "🇫🇮 Finnish", "ko": "🇰🇷 Korean",
    "no": "🇳🇴 Norwegian", "pl": "🇵🇱 Polish", "id": "🇮🇩 Indonesian",
    "xx": "🌍 Unknown",
}


SORT_OPTIONS: dict[str, tuple[str, bool]] = {
    "Rating (High → Low)": ("avg_rating", False),
    "Rating (Low → High)": ("avg_rating", True),
    "Year (Newest)": ("release_year", False),
    "Year (Oldest)": ("release_year", True),
    "Title (A → Z)": ("title", True),
}
