import functions_framework
import os
import pandas as pd
from google.cloud import bigquery
from flask import jsonify

# To deploy: 
# 1. Ensure 'google-cloud-bigquery' and 'pandas' are in your requirements.txt
# 2. Set TMDB_API_KEY as an env var in the Cloud Function console.

client = bigquery.Client()

@functions_framework.http
def get_movie_titles(request):
    """
    Gold Standard Cloud Function using BigQuery for the 20M Movie Dataset.
    This replaces the local CSV logic and connects directly to your GCP data.
    """
    try:
        # Example query - update with your actual project.dataset.table names
        query = """
            SELECT 
                movieId, title, genres, release_year, language,
                CAST(avg_rating AS FLOAT64) as avg_rating
            FROM `your-project-id.your_dataset.merged_movies_20m`
            ORDER BY release_year DESC
            LIMIT 1000
        """
        
        # Note: If you haven't deployed the BigQuery table yet, 
        # this function will fail gracefully and the app will use TMDB fallback.
        query_job = client.query(query)
        results = query_job.to_dataframe()

        if results.empty:
            return jsonify({'error': 'No matching movies found in BigQuery.'}), 404

        # Convert to list of dicts for JSON serialization
        movie_details = results.to_dict(orient='records')
        return jsonify({'movie_details': movie_details})

    except Exception as e:
        # Log the error for GCP Monitoring
        print(f"Error: {str(e)}")
        # Return a message that triggers the frontend fallback logic if desired
        return jsonify({'error': f"BigQuery error: {str(e)}"}), 500
