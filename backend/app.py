"""
Flask backend for the Movie Recommender application.

Endpoints:
  GET  /               → health check
  GET  /movies         → all movies from BigQuery
  GET  /autocomplete   → Elasticsearch autocomplete suggestions
  GET  /trending       → most-rated movies with TMDB posters
  GET  /top-rated      → highest-rated movies with TMDB posters
  POST /recommend      → cold-start recommendations based on selected movies
  POST /setup/index    → (admin) index all movies in Elasticsearch
  POST /train          → (admin) train BigQuery ML matrix factorization model
"""

import os
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests as http_requests
from flask import Flask, jsonify, request
from flask_cors import CORS

from config import (
    BQ_PROJECT_ID,
    BQ_DATASET,
    TMDB_API_KEY,
    ELASTICSEARCH_URL,
    ELASTICSEARCH_API_KEY,
    ELASTICSEARCH_PASSWORD,
    ES_INDEX,
)
from bigquery_client import BigQueryClient
from elasticsearch_client import ElasticsearchClient

app = Flask(__name__)
CORS(app)

bq = BigQueryClient(BQ_PROJECT_ID, BQ_DATASET)
es = ElasticsearchClient(ELASTICSEARCH_URL, ELASTICSEARCH_API_KEY, ELASTICSEARCH_PASSWORD, ES_INDEX)


# ──────────────────────────────────────────────────────────────────────
# Health
# ──────────────────────────────────────────────────────────────────────

@app.route("/")
def health():
    return jsonify({
        "status": "ok",
        "service": "movie-recommender-backend",
        "bigquery_project": BQ_PROJECT_ID,
        "bigquery_dataset": BQ_DATASET,
        "elasticsearch": es.health(),
    })


# ──────────────────────────────────────────────────────────────────────
# Movie catalog
# ──────────────────────────────────────────────────────────────────────

@app.route("/movies")
def get_movies():
    """Return all movies (no poster enrichment — used for autocomplete seeding)."""
    movies = bq.get_all_movies()
    return jsonify(movies)


@app.route("/trending")
def trending():
    limit = _clamp(request.args.get("limit", 24), 1, 50)
    movies = bq.get_trending_movies(limit)
    return jsonify(_enrich_posters(movies))


@app.route("/top-rated")
def top_rated():
    limit = _clamp(request.args.get("limit", 24), 1, 50)
    movies = bq.get_global_recommendations(limit)
    return jsonify(_enrich_posters(movies))


# ──────────────────────────────────────────────────────────────────────
# Autocomplete (Elasticsearch)
# ──────────────────────────────────────────────────────────────────────

@app.route("/autocomplete")
def autocomplete():
    q = request.args.get("q", "").strip()
    if len(q) < 2:
        return jsonify([])
    results = es.autocomplete(q, size=8)
    return jsonify(results)


# ──────────────────────────────────────────────────────────────────────
# Recommendations (cold-start collaborative filtering)
# ──────────────────────────────────────────────────────────────────────

@app.route("/recommend", methods=["POST"])
def recommend():
    """
    Body (JSON):
      { "movie_ids": [1, 2, 3], "top_n": 20 }

    If movie_ids is empty → return global top recommendations.
    Otherwise → cold-start similarity-based recommendations.
    """
    data = request.get_json(silent=True) or {}
    movie_ids = [int(m) for m in data.get("movie_ids", [])]
    top_n = _clamp(data.get("top_n", 20), 1, 50)

    if not movie_ids:
        recs = bq.get_global_recommendations(top_n)
    else:
        recs = bq.get_cold_start_recommendations(movie_ids, top_n)

    return jsonify(_enrich_posters(recs))


# ──────────────────────────────────────────────────────────────────────
# Admin / setup endpoints
# ──────────────────────────────────────────────────────────────────────

@app.route("/setup/index", methods=["POST"])
def setup_index():
    """Fetch all movies from BigQuery and index them in Elasticsearch."""
    movies = bq.get_all_movies()
    es.index_movies(movies)
    return jsonify({"status": "indexed", "count": len(movies)})


@app.route("/train", methods=["POST"])
def train():
    """Train the BigQuery ML matrix factorization recommendation model."""
    result = bq.train_model()
    return jsonify({"status": result})


# ──────────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────────

def _get_tmdb_data(tmdb_id) -> dict:
    """Fetch poster + backdrop URLs and overview from TMDB for one movie."""
    if not TMDB_API_KEY or not tmdb_id:
        return {}
    try:
        resp = http_requests.get(
            f"https://api.themoviedb.org/3/movie/{int(tmdb_id)}",
            params={"api_key": TMDB_API_KEY},
            timeout=6,
        )
        resp.raise_for_status()
        d = resp.json()
        base = "https://image.tmdb.org/t/p"
        return {
            "poster_url":   f"{base}/w500{d['poster_path']}"   if d.get("poster_path")   else None,
            "backdrop_url": f"{base}/w1280{d['backdrop_path']}" if d.get("backdrop_path") else None,
            "overview":     d.get("overview", ""),
            "vote_average": d.get("vote_average", 0),
        }
    except Exception:
        return {}


def _enrich_posters(movies: list[dict]) -> list[dict]:
    """Parallel TMDB poster enrichment for a list of movies."""
    if not TMDB_API_KEY:
        for m in movies:
            m.update({"poster_url": None, "backdrop_url": None, "overview": ""})
        return movies

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(_get_tmdb_data, m.get("tmdbId")): i
            for i, m in enumerate(movies)
        }
        for future in as_completed(futures):
            idx = futures[future]
            try:
                movies[idx].update(future.result())
            except Exception:
                pass

    for m in movies:
        m.setdefault("poster_url", None)
        m.setdefault("backdrop_url", None)
        m.setdefault("overview", "")
    return movies


def _clamp(value, lo, hi) -> int:
    try:
        return max(lo, min(int(value), hi))
    except (TypeError, ValueError):
        return lo


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"[Flask] Starting on port {port}")
    print(f"[Flask] BigQuery project: {BQ_PROJECT_ID}, dataset: {BQ_DATASET}")
    print(f"[Flask] Elasticsearch: {ELASTICSEARCH_URL}")
    app.run(host="0.0.0.0", port=port, debug=False)
