import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")
load_dotenv(Path(__file__).parent.parent / ".env")

BQ_PROJECT_ID: str = os.environ.get("BQ_PROJECT_ID", "assignment-1-489109")
BQ_DATASET: str = os.environ.get("BQ_DATASET", "movielens")

TMDB_API_KEY: str = os.environ.get("TMDB_API_KEY", "") or os.environ.get("TMDB_API_key", "")

ELASTICSEARCH_URL: str = os.environ.get("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_API_KEY: str = os.environ.get("ELASTICSEARCH_API_KEY", "")
ELASTICSEARCH_PASSWORD: str = os.environ.get("ELASTICSEARCH_PASSWORD", "")
ES_INDEX: str = os.environ.get("ELASTICSEARCH_INDEX", "movies")
