from google.cloud import bigquery
import pandas as pd


class BigQueryClient:
    """Handles all BigQuery operations for the movie recommender backend."""

    def __init__(self, project_id: str, dataset: str):
        self.client = bigquery.Client(project=project_id)
        self.project = project_id
        self.dataset = dataset

    def _t(self, table: str) -> str:
        """Return fully-qualified table reference."""
        return f"`{self.project}.{self.dataset}.{table}`"

    # ──────────────────────────────────────────────────────────────────
    # Movie catalog
    # ──────────────────────────────────────────────────────────────────

    def get_all_movies(self) -> list[dict]:
        """Return all movies with average rating and TMDB link."""
        query = f"""
            SELECT
                m.movieId,
                m.title,
                m.genres,
                SAFE_CAST(REGEXP_EXTRACT(m.title, r'\\((\\d{{4}})\\)') AS INT64) AS release_year,
                ROUND(AVG(CAST(r.rating AS FLOAT64)), 2) AS avg_rating,
                l.tmdbId
            FROM {self._t('movies')} m
            LEFT JOIN {self._t('ratings')} r ON m.movieId = r.movieId
            LEFT JOIN {self._t('links')}   l ON m.movieId = l.movieId
            GROUP BY m.movieId, m.title, m.genres, l.tmdbId
            ORDER BY avg_rating DESC NULLS LAST
        """
        print(f"\n[BigQuery] get_all_movies\n{'─'*60}\n{query.strip()}\n{'─'*60}")
        df = self.client.query(query).to_dataframe()
        print(f"[BigQuery] → {len(df)} movies returned\n")
        return df.fillna(0).to_dict(orient="records")

    def get_trending_movies(self, limit: int = 24) -> list[dict]:
        """Most-rated movies (popularity proxy)."""
        query = f"""
            SELECT
                m.movieId,
                m.title,
                m.genres,
                SAFE_CAST(REGEXP_EXTRACT(m.title, r'\\((\\d{{4}})\\)') AS INT64) AS release_year,
                ROUND(AVG(CAST(r.rating AS FLOAT64)), 2) AS avg_rating,
                COUNT(r.rating) AS num_ratings,
                l.tmdbId
            FROM {self._t('movies')} m
            JOIN {self._t('ratings')} r ON m.movieId = r.movieId
            LEFT JOIN {self._t('links')} l ON m.movieId = l.movieId
            GROUP BY m.movieId, m.title, m.genres, l.tmdbId
            HAVING COUNT(r.rating) >= 50
            ORDER BY num_ratings DESC
            LIMIT {limit}
        """
        print(f"\n[BigQuery] get_trending_movies (limit={limit})\n{'─'*60}\n{query.strip()}\n{'─'*60}")
        df = self.client.query(query).to_dataframe()
        print(f"[BigQuery] → {len(df)} trending movies returned\n")
        return df.fillna(0).to_dict(orient="records")

    def get_global_recommendations(self, top_n: int = 24) -> list[dict]:
        """Best-rated movies with sufficient votes — used when no preferences given."""
        query = f"""
            SELECT
                m.movieId,
                m.title,
                m.genres,
                SAFE_CAST(REGEXP_EXTRACT(m.title, r'\\((\\d{{4}})\\)') AS INT64) AS release_year,
                ROUND(AVG(CAST(r.rating AS FLOAT64)), 2) AS avg_rating,
                COUNT(r.rating) AS num_ratings,
                l.tmdbId
            FROM {self._t('movies')} m
            JOIN {self._t('ratings')} r ON m.movieId = r.movieId
            LEFT JOIN {self._t('links')} l ON m.movieId = l.movieId
            GROUP BY m.movieId, m.title, m.genres, l.tmdbId
            HAVING COUNT(r.rating) >= 100
            ORDER BY avg_rating DESC, num_ratings DESC
            LIMIT {top_n}
        """
        print(f"\n[BigQuery] get_global_recommendations (top_n={top_n})\n{'─'*60}\n{query.strip()}\n{'─'*60}")
        df = self.client.query(query).to_dataframe()
        print(f"[BigQuery] → {len(df)} global recommendations returned\n")
        return df.fillna(0).to_dict(orient="records")

    # ──────────────────────────────────────────────────────────────────
    # Cold-start recommendations
    # ──────────────────────────────────────────────────────────────────

    def get_cold_start_recommendations(
        self, movie_ids: list[int], top_n: int = 24
    ) -> list[dict]:
        """
        Cold-start collaborative filtering:
          1. Find users who rated ≥1 of the selected movies highly (≥3.5/5).
          2. Rank users by number of matching preferred movies (most similar first).
          3. Collect movies highly rated (≥4.0) by those similar users.
          4. Exclude already-selected movies and rank by # of similar-user endorsements.
        """
        ids_str = ", ".join(str(int(m)) for m in movie_ids)

        query = f"""
            -- Step 1: find similar users ranked by overlap with the user's selection
            WITH similar_users AS (
                SELECT
                    r.userId,
                    COUNT(DISTINCT r.movieId)            AS common_movies,
                    AVG(CAST(r.rating AS FLOAT64))       AS avg_rating_given
                FROM {self._t('ratings')} r
                WHERE r.movieId IN ({ids_str})
                  AND CAST(r.rating AS FLOAT64) >= 3.5
                GROUP BY r.userId
                ORDER BY common_movies DESC, avg_rating_given DESC
                LIMIT 30
            ),
            -- Step 2: collect candidate movies from similar users
            candidates AS (
                SELECT
                    r.movieId,
                    COUNT(DISTINCT r.userId)         AS similar_user_votes,
                    AVG(CAST(r.rating AS FLOAT64))   AS avg_rating
                FROM {self._t('ratings')} r
                JOIN similar_users su ON r.userId = su.userId
                WHERE r.movieId NOT IN ({ids_str})
                  AND CAST(r.rating AS FLOAT64) >= 3.5
                GROUP BY r.movieId
            )
            -- Step 3: enrich with movie metadata and links
            SELECT
                m.movieId,
                m.title,
                m.genres,
                SAFE_CAST(REGEXP_EXTRACT(m.title, r'\\((\\d{{4}})\\)') AS INT64) AS release_year,
                ROUND(c.avg_rating, 2)   AS avg_rating,
                c.similar_user_votes,
                l.tmdbId
            FROM candidates c
            JOIN {self._t('movies')} m ON c.movieId = m.movieId
            LEFT JOIN {self._t('links')} l ON c.movieId = l.movieId
            ORDER BY c.similar_user_votes DESC, c.avg_rating DESC
            LIMIT {top_n}
        """
        print(
            f"\n[BigQuery] get_cold_start_recommendations"
            f" (input_movies={movie_ids}, top_n={top_n})\n{'─'*60}\n{query.strip()}\n{'─'*60}"
        )
        df = self.client.query(query).to_dataframe()
        print(f"[BigQuery] → {len(df)} recommendations returned\n")
        return df.fillna(0).to_dict(orient="records")

    # ──────────────────────────────────────────────────────────────────
    # BigQuery ML
    # ──────────────────────────────────────────────────────────────────

    def train_model(self) -> str:
        """Train a BigQuery ML matrix factorization model."""
        model_ref = f"`{self.project}.{self.dataset}.movie_recommender`"
        query = f"""
            CREATE OR REPLACE MODEL {model_ref}
            OPTIONS (
                model_type      = 'matrix_factorization',
                user_col        = 'userId',
                item_col        = 'movieId',
                rating_col      = 'rating',
                feedback_type   = 'explicit',
                num_factors     = 16,
                l2_reg          = 0.1
            ) AS
            SELECT
                CAST(userId  AS STRING) AS userId,
                CAST(movieId AS STRING) AS movieId,
                CAST(rating  AS FLOAT64) AS rating
            FROM {self._t('ratings')}
        """
        print(f"\n[BigQuery ML] Training matrix factorization model…\n{'─'*60}\n{query.strip()}\n{'─'*60}")
        job = self.client.query(query)
        job.result()
        print("[BigQuery ML] ✓ Model training complete\n")
        return "Model trained successfully"

    def get_ml_recommendations(self, user_id: str, top_n: int = 20) -> list[dict]:
        """Get recommendations from the trained BQML model for a given user."""
        model_ref = f"`{self.project}.{self.dataset}.movie_recommender`"
        query = f"""
            SELECT
                rec.movieId,
                m.title,
                m.genres,
                SAFE_CAST(REGEXP_EXTRACT(m.title, r'\\((\\d{{4}})\\)') AS INT64) AS release_year,
                ROUND(rec.predicted_rating_im_mean, 2) AS predicted_rating,
                l.tmdbId
            FROM ML.RECOMMEND(
                MODEL {model_ref},
                (SELECT CAST('{user_id}' AS STRING) AS userId)
            ) rec
            JOIN {self._t('movies')} m
              ON CAST(rec.movieId AS STRING) = CAST(m.movieId AS STRING)
            LEFT JOIN {self._t('links')} l ON m.movieId = l.movieId
            ORDER BY rec.predicted_rating_im_mean DESC
            LIMIT {top_n}
        """
        print(f"\n[BigQuery ML] get_ml_recommendations (user={user_id})\n{'─'*60}\n{query.strip()}\n{'─'*60}")
        df = self.client.query(query).to_dataframe()
        print(f"[BigQuery ML] → {len(df)} ML recommendations returned\n")
        return df.fillna(0).to_dict(orient="records")
