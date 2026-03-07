import functions_framework
import os
import pandas as pd
from google.cloud import bigquery
from flask import jsonify

client = bigquery.Client()

@functions_framework.http
def get_movie_titles(request):
    """
    Gold Standard Cloud Function using BigQuery for the 20M Movie Dataset.
    This replaces the local CSV logic and connects directly to your GCP data.
    """
    try:
        query = """
            SELECT
                movieId, title, genres, release_year, language,
                CAST(avg_rating AS FLOAT64) as avg_rating
            FROM `your-project-id.your_dataset.merged_movies_20m`
            ORDER BY release_year DESC
        """

        query_job = client.query(query)
        results = query_job.to_dataframe()

        if results.empty:
            return jsonify({'error': 'No matching movies found in BigQuery.'}), 404

        movie_details = results.to_dict(orient='records')
        return jsonify({'movie_details': movie_details})

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({'error': f"BigQuery error: {str(e)}"}), 500
