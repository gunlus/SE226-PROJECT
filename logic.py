import requests
from bs4 import BeautifulSoup
from imdb import Cinemagoer
import google.generativeai as genai
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

# IMDb Scraping
def fetch_imdb_top_10():
    ia = Cinemagoer()
    top_movies = ia.get_top250_movies()
    print("Fetched movie count:", len(top_movies))  # Debug

    return [
        (movie['title'], f"https://www.imdb.com/title/tt{movie.movieID}/")
        for movie in top_movies[:10]
    ]



# Storyline Fetching
def get_movie_storyline(title):
    ia = Cinemagoer()
    movies = ia.search_movie(title)
    if movies:
        movie = ia.get_movie(movies[0].movieID)
        return movie.get('plot outline', "No storyline available.")
    return "Movie not found"

# Gemini API (set your API key here)
genai.configure(api_key="AIzaSyCtTPtcczd13x5K-VHHP6WaRMIknvlmtoY")
model = genai.GenerativeModel(model_name="gemini-pro")

def generate_dialogue_gemini(storyline, num_characters, word_limit):
    prompt = f"Create a {word_limit}-word dialogue with {num_characters} characters. Storyline: {storyline}"
    response = model.generate_content(prompt)
    return response.text

# Vertex AI (setup project ID)
vertexai.init(project="dark-yen-459418-k4", location="us-central1")

print("Vertex AI initialized successfully!")

def generate_image_vertex(prompt):
    img_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
    response = img_model.generate_images(prompt=prompt, number_of_images=1)
    return response.images[0]
