import logging
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk

logger = logging.getLogger(__name__)


class ElasticsearchClient:
    """Thin wrapper around the Elasticsearch Python client for movie autocomplete."""

    def __init__(self, url: str, api_key: str = "", password: str = "", index: str = "movies"):
        if api_key:
            self.es = Elasticsearch(url, api_key=api_key, verify_certs=True)
        elif password:
            self.es = Elasticsearch(url, basic_auth=("elastic", password))
        else:
            self.es = Elasticsearch(url)
        self.index = index

    # ──────────────────────────────────────────────────────────────────
    # Index management
    # ──────────────────────────────────────────────────────────────────

    def create_index(self) -> None:
        """Create the movies index with search-as-you-type mapping."""
        mapping = {
            "mappings": {
                "properties": {
                    "movieId":      {"type": "integer"},
                    "release_year": {"type": "integer"},
                    "avg_rating":   {"type": "float"},
                    "genres":       {"type": "keyword"},
                    "title": {
                        "type": "search_as_you_type",
                        "analyzer": "standard",
                    },
                }
            }
        }
        if not self.es.indices.exists(index=self.index):
            self.es.indices.create(index=self.index, body=mapping)
            print(f"[Elasticsearch] Created index '{self.index}'")
        else:
            print(f"[Elasticsearch] Index '{self.index}' already exists — skipping creation")

    def index_movies(self, movies: list[dict]) -> None:
        """Bulk-index all movies into Elasticsearch for autocomplete."""
        self.create_index()
        actions = [
            {
                "_index": self.index,
                "_id": str(m["movieId"]),
                "_source": {
                    "movieId":      m["movieId"],
                    "title":        m["title"],
                    "genres":       m.get("genres", ""),
                    "release_year": m.get("release_year") or 0,
                    "avg_rating":   m.get("avg_rating") or 0.0,
                },
            }
            for m in movies
            if m.get("movieId") and m.get("title")
        ]
        success, errors = bulk(self.es, actions, raise_on_error=False)
        print(f"[Elasticsearch] Indexed {success} documents, {len(errors)} errors")
        if errors:
            for e in errors[:5]:
                print(f"  ↳ {e}")

    # ──────────────────────────────────────────────────────────────────
    # Search / autocomplete
    # ──────────────────────────────────────────────────────────────────

    def autocomplete(self, query: str, size: int = 8) -> list[dict]:
        """
        Return autocomplete suggestions using Elasticsearch's
        search-as-you-type field type (fast prefix + infix matching).
        """
        try:
            body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "type": "bool_prefix",
                        "fields": [
                            "title",
                            "title._2gram",
                            "title._3gram",
                        ],
                    }
                },
                "_source": ["movieId", "title", "genres", "release_year", "avg_rating"],
                "size": size,
            }
            resp = self.es.search(index=self.index, body=body)
            hits = resp["hits"]["hits"]
            print(f"[Elasticsearch] autocomplete('{query}') → {len(hits)} hits")
            return [h["_source"] for h in hits]
        except Exception as exc:
            logger.error("Elasticsearch autocomplete error: %s", exc)
            return []

    def health(self) -> dict:
        try:
            info = self.es.cluster.health()
            return {"status": info.get("status", "unknown")}
        except Exception as exc:
            return {"status": "error", "detail": str(exc)}
