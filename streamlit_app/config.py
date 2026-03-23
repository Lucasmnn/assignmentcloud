import os
from pathlib import Path
from dotenv import load_dotenv

_app_dir = Path(__file__).resolve().parent
load_dotenv(_app_dir / ".env")
load_dotenv(_app_dir.parent / ".env")

# ── Backend API (Flask) ─────────────────────────────────────────────
BACKEND_URL: str = os.environ.get(
    "BACKEND_URL", "http://localhost:8080"
)

# ── TMDB (used for fallback poster fetch in frontend, optional) ─────
TMDB_API_KEY: str = os.environ.get("TMDB_API_KEY", "") or os.environ.get("TMDB_API_key", "")
TMDB_IMG_BASE: str = "https://image.tmdb.org/t/p/w500"

# ── UI constants ────────────────────────────────────────────────────
MOVIES_PER_PAGE: int = 24
APP_TITLE: str = "MovieFlix"

# ── (Legacy) Direct BigQuery — used only by the old Part-1 data.py ──
BQ_PROJECT_ID: str = os.environ.get("BQ_PROJECT_ID", "assignment-1-489109")
BQ_TABLE_ID: str   = os.environ.get("BQ_TABLE_ID",   "assignment1.Movie")

# ── Genre / sort / language maps kept for any util references ───────
GENRE_CSS_MAP: dict[str, str] = {
    "Drama": "drama", "Comedy": "comedy", "Action": "action",
    "Romance": "romance", "Thriller": "thriller", "Horror": "horror",
    "Sci-Fi": "sci-fi", "Adventure": "adventure", "Animation": "animation",
    "Musical": "musical", "War": "war", "Crime": "crime",
    "Mystery": "mystery", "Documentary": "documentary", "Western": "western",
    "Fantasy": "fantasy", "Children": "children", "Film-Noir": "film-noir",
}
