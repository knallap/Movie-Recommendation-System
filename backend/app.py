from flask import Flask, request, jsonify
import pickle
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Load the movie list and similarity matrix
try:
    movies = pickle.load(open('model/movie_list.pkl', 'rb'))
    similarity = pickle.load(open('model/similarity.pkl', 'rb'))
    print("Models loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    movies, similarity = None, None

@app.route('/movies', methods=['GET'])
def get_movies():
    """Endpoint to get the list of movies."""
    if movies is None:
        return jsonify({"error": "Movies dataset not loaded"}), 500
    return jsonify({"movies": movies['title'].tolist()})

@app.route('/recommend', methods=['POST'])
def recommend():
    """Endpoint to get movie recommendations."""
    try:
        data = request.json
        movie = data.get('movie')

        # Validate input
        if not movie:
            return jsonify({"error": "No movie provided"}), 400

        # Check if the movie exists in the dataset
        if movie not in movies['title'].values:
            return jsonify({"error": f"Movie '{movie}' not found in the dataset"}), 404

        # Find the index of the movie
        index = movies[movies['title'] == movie].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])

        # Generate top-5 recommendations
        recommendations = []
        for i in distances[1:4]:
            movie_id = movies.iloc[i[0]].movie_id
            recommendations.append({
                "title": movies.iloc[i[0]].title,
                "poster": fetch_poster(movie_id)
            })

        return jsonify({"recommendations": recommendations})

    except Exception as e:
        print(f"Error in recommend(): {e}")
        return jsonify({"error": "Internal server error"}), 500

def fetch_poster(movie_id):
    """Fetch movie poster using TMDb API."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP responses
        data = response.json()
        poster_path = data.get('poster_path')

        if not poster_path:
            print(f"No poster found for movie ID {movie_id}")
            return ""  # Return an empty string if no poster is found

        return f"https://image.tmdb.org/t/p/w500/{poster_path}"

    except Exception as e:
        print(f"Error in fetch_poster(): {e}")
        return ""  # Return an empty string in case of an error

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
