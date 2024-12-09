from flask import Flask, request, jsonify
import pickle
import requests
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Dropbox links for `.pkl` files
MOVIE_LIST_URL = "https://www.dropbox.com/scl/fi/fcicgh7nrbisb2gzrsy48/movie_list.pkl?rlkey=cstc7fhq1mdv1i616p0je7ie4&st=3go1e0l7&dl=1"
SIMILARITY_MATRIX_URL = "https://www.dropbox.com/scl/fi/3q3ae70rojiziwbx924em/similarity.pkl?rlkey=wq34cs7o9llj4dicxj2vrgro7&st=bfu6s6c6&dl=1"

# Local paths for downloaded files
MOVIE_LIST_FILE = "movie_list.pkl"
SIMILARITY_FILE = "similarity.pkl"

def download_file(url, local_filename):
    """Download a file from Dropbox if it doesn't exist locally."""
    if not os.path.exists(local_filename):
        print(f"Downloading {local_filename} from {url}...")
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            with open(local_filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Downloaded {local_filename}")
        else:
            raise Exception(f"Failed to download {local_filename}. Status code: {response.status_code}")
    else:
        print(f"{local_filename} already exists. Skipping download.")

# Ensure required files are downloaded
try:
    download_file(MOVIE_LIST_URL, MOVIE_LIST_FILE)
    download_file(SIMILARITY_MATRIX_URL, SIMILARITY_FILE)

    # Load the movie list and similarity matrix
    print("Loading movie list...")
    with open(MOVIE_LIST_FILE, 'rb') as f:
        movies = pickle.load(f, encoding="latin1")  # Add encoding to handle compatibility
    print("Movie list loaded successfully.")

    print("Loading similarity matrix...")
    with open(SIMILARITY_FILE, 'rb') as f:
        similarity = pickle.load(f, encoding="latin1")
    print("Similarity matrix loaded successfully.")
except Exception as e:
    print(f"Error loading models: {e}")
    movies, similarity = None, None

@app.route("/", methods=["GET"])
def home():
    """Health check route."""
    return jsonify({"status": "Running"})

@app.route("/movies", methods=["GET"])
def get_movies():
    """Endpoint to get the list of movies."""
    try:
        if movies is None:
            return jsonify({"error": "Movies dataset not loaded"}), 500
        return jsonify({"movies": movies['title'].tolist()})
    except Exception as e:
        print(f"Error in /movies endpoint: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/recommend", methods=["POST"])
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
    app.run(host="0.0.0.0", port=5000, debug=True)
