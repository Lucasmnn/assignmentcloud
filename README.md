# MovieFlix — Cloud & Advanced Analytics 2025

## Live Application

| Service | URL |
|---------|-----|
| **Frontend (Streamlit)** | *(deploy URL — update after Cloud Run deployment)* |
| **Backend (Flask)**      | *(deploy URL — update after Cloud Run deployment)* |

---

## Architecture

```
┌─────────────────────┐     REST API     ┌──────────────────────────┐
│  Streamlit Frontend │ ───────────────► │     Flask Backend         │
│  (Cloud Run)        │                  │     (Cloud Run)           │
└─────────────────────┘                  │                          │
                                         │  ┌────────────────────┐  │
                                         │  │   BigQuery         │  │
                                         │  │  (movies/ratings/  │  │
                                         │  │   links + BQML)    │  │
                                         │  └────────────────────┘  │
                                         │                          │
                                         │  ┌────────────────────┐  │
                                         │  │  Elasticsearch     │  │
                                         │  │  (autocomplete)    │  │
                                         │  └────────────────────┘  │
                                         │                          │
                                         │  ┌────────────────────┐  │
                                         │  │   TMDB API         │  │
                                         │  │  (movie posters)   │  │
                                         │  └────────────────────┘  │
                                         └──────────────────────────┘
```

---

## Similarity Computation Method

The application solves the **cold-start problem** using collaborative filtering similarity:

1. **User selects movies** they have enjoyed (the "preference set").
2. **Find similar users**: query BigQuery for users who rated ≥1 of the selected movies with a score ≥ 3.5/5. Rank them by **number of matching preferred movies** (descending), then by their average rating (tie-break). Keep the top-30 most similar users.
3. **Collect candidate movies**: aggregate movies that these similar users rated ≥ 3.5, excluding movies the user already selected. Score each candidate by the **count of similar users who endorsed it**.
4. **Rank and return**: sort by endorsement count then average rating, return the top-N.

**Example** (from the assignment):

| User | Highly rated |
|------|-------------|
| u1   | [2, 4, 6, 8, 9] |
| u2   | [1, 3, 7, 9]    |
| u3   | [3, 5, 8, 9]    |
| u4   | [7, 8, 9]       |

If the app user selects `[1, 3, 5, 7]`:
- u2 matches 3 movies → most similar
- u3 matches 2 movies
- u4 matches 1 movie
- u1 matches 0 movies

Movies highly rated by u2 (then u3, u4) that are not in the selection are recommended.

---

## Project Structure

```
├── backend/                    # Flask REST API
│   ├── app.py                  # API endpoints
│   ├── bigquery_client.py      # BigQuery + BQML queries (printed to terminal)
│   ├── elasticsearch_client.py # ES indexing + autocomplete
│   ├── config.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
│
├── streamlit_app/              # Netflix-style Streamlit UI
│   ├── app.py                  # Main Netflix UI
│   ├── api_client.py           # Backend API calls
│   ├── styles.py               # Netflix CSS
│   ├── config.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml          # Local development (ES + backend + frontend)
└── README.md
```

---

## Local Development

### Prerequisites
- Docker & Docker Compose
- GCP service account with BigQuery access
- TMDB API key
- Elasticsearch (included in Docker Compose)

### 1. Configure environment

```bash
cp backend/.env.example .env
# Edit .env with your credentials
```

### 2. Start all services

```bash
docker-compose up --build
```

- Frontend: http://localhost:8501
- Backend:  http://localhost:8080

### 3. Index movies in Elasticsearch (run once)

```bash
curl -X POST http://localhost:8080/setup/index
```

### 4. (Optional) Train BigQuery ML model

```bash
curl -X POST http://localhost:8080/train
```

---

## BigQuery Setup (Part 2)

Upload the ml-25m-small dataset to BigQuery. Create a dataset (e.g. `movielens`) with three tables:

```sql
-- movies (movieId INT64, title STRING, genres STRING)
-- ratings (userId INT64, movieId INT64, rating FLOAT64, timestamp INT64)
-- links (movieId INT64, imdbId INT64, tmdbId INT64)
```

All executed SQL queries and their results are printed to the terminal during runtime.

---

## Deployment on Cloud Run

### Backend

```bash
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/movieflix-backend
gcloud run deploy movieflix-backend \
  --image gcr.io/PROJECT_ID/movieflix-backend \
  --platform managed --region europe-west1 \
  --set-env-vars "BQ_PROJECT_ID=...,BQ_DATASET=movielens,TMDB_API_KEY=...,ELASTICSEARCH_URL=..."
```

### Frontend

```bash
cd streamlit_app
gcloud builds submit --tag gcr.io/PROJECT_ID/movieflix-frontend
gcloud run deploy movieflix-frontend \
  --image gcr.io/PROJECT_ID/movieflix-frontend \
  --platform managed --region europe-west1 \
  --set-env-vars "BACKEND_URL=https://movieflix-backend-xxx.run.app"
```

---

## Expected Terminal Output

Every BigQuery query is printed to stdout with its SQL and row-count result:

```
[BigQuery] get_cold_start_recommendations (input_movies=[1, 2, 3], top_n=20)
────────────────────────────────────────────────────────────
WITH similar_users AS (
    SELECT r.userId, COUNT(DISTINCT r.movieId) AS common_movies, ...
...
────────────────────────────────────────────────────────────
[BigQuery] → 20 recommendations returned

[Elasticsearch] autocomplete('inc') → 5 hits
```
