import functions_framework
import requests
import os
from flask import jsonify

# Load API key from environment for Cloud Function deployment
# (Can be set in GCP Console > Edit Function > Runtime environment variables)
TMDB_API_KEY = os.environ.get("TMDB_API_KEY", "")

@functions_framework.http
def get_movie_titles(request):
    """
    Original Cloud Function 1 from Lab 1 Notebook.
    Fetches a list of discoverable movies from TMDB.
    """
    try:
        movie_database_url = 'https://api.themoviedb.org/3/discover/movie'
        api_key = TMDB_API_KEY or request.args.get('api_key', '')

        if not api_key:
            return jsonify({'error': 'Missing TMDB API Key. Set TMDB_API_KEY env var.'}), 401

        # Fetch 3 pages of results to have a decent catalog (~60 movies)
        all_results = []
        for page in range(1, 4):
            response = requests.get(
                movie_database_url, 
                params={'api_key': api_key, 'page': page, 'sort_by': 'popularity.desc'},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            if 'results' in data:
                all_results.extend(data['results'])

        if not all_results:
            return jsonify({'error': 'No results found.'}), 404

        # Filter and format exactly as the old app expects
        movies_with_poster = [m for m in all_results if m.get('poster_path')]
        
        # Add required fields for the Streamlit app's logic
        movie_details = []
        for m in movies_with_poster:
            movie_details.append({
                'movieId': m['id'],
                'title': m['title'],
                'release_year': int(m['release_date'][:4]) if m.get('release_date') else 0,
                'avg_rating': m.get('vote_average', 0.0),
                'genres': "|".join([str(gid) for gid in m.get('genre_ids', [])]), # Simplified genres
                'language': m.get('original_language', 'xx')
            })

        return jsonify({'movie_details': movie_details})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
