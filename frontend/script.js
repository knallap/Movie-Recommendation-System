let movieList = [];

// Fetch the movie list from the backend
window.onload = async function () {
  try {
    const response = await fetch("http://localhost:5000/movies");
    if (!response.ok) throw new Error("Failed to fetch movie list.");
    const data = await response.json();
    movieList = data.movies; // Load the movie list
  } catch (error) {
    console.error(error);
    alert("Error fetching movie list.");
  }
};

// Show suggestions as the user types
document.getElementById("searchInput").addEventListener("input", function () {
  const input = this.value.toLowerCase();
  const suggestionsDiv = document.getElementById("suggestions");
  suggestionsDiv.innerHTML = "";

  if (input) {
    const filteredMovies = movieList.filter((movie) =>
      movie.toLowerCase().includes(input)
    );

    filteredMovies.slice(0, 10).forEach((movie) => {
      const div = document.createElement("div");
      div.textContent = movie;
      div.addEventListener("click", function () {
        document.getElementById("searchInput").value = movie;
        suggestionsDiv.innerHTML = "";
        suggestionsDiv.style.display = "none";
      });
      suggestionsDiv.appendChild(div);
    });
    suggestionsDiv.style.display = "block";
  } else {
    suggestionsDiv.style.display = "none";
  }
});

// Fetch recommendations on search button click
document.getElementById("searchButton").addEventListener("click", async function () {
  const movieName = document.getElementById("searchInput").value;

  if (!movieName) {
    alert("Please enter a movie name.");
    return;
  }

  try {
    const response = await fetch("http://localhost:5000/recommend", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ movie: movieName }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      alert(`Error: ${errorData.error}`);
      return;
    }

    const data = await response.json();
    showMovieModal(data.recommendations);
  } catch (error) {
    console.error("Error during fetch:", error);
    alert("Error fetching recommendations.");
  }
});

// Function to display movies in a modal popup
function showMovieModal(recommendations) {
  const modal = document.getElementById("movieModal");
  const modalMovies = document.getElementById("modalMovies");

  // Clear previous recommendations
  modalMovies.innerHTML = "";

  if (recommendations.length === 0) {
    modalMovies.innerHTML = "<p>No recommendations found.</p>";
  } else {
    recommendations.forEach((movie) => {
      const movieDiv = document.createElement("div");
      movieDiv.className = "modal-movie";

      const img = document.createElement("img");
      img.src = movie.poster;
      img.alt = movie.title;

      const title = document.createElement("p");
      title.className = "modal-movie-title";
      title.textContent = movie.title;

      movieDiv.appendChild(img);
      movieDiv.appendChild(title);
      modalMovies.appendChild(movieDiv);
    });
  }

  // Show the modal
  modal.style.display = "block";

  // Close the modal when the close button is clicked
  document.querySelector(".close").onclick = function () {
    modal.style.display = "none";
  };

  // Close the modal when clicking outside the content
  window.onclick = function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };
}
