from imdb import Cinemagoer
import requests
from bs4 import BeautifulSoup

def get_top_10_movies():
    url = "https://www.imdb.com/chart/top/"
    headers = {
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    print("Status code:", response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')

    print("Trying to find movie names")
    movies = soup.select("a.ipc-title-link-wrapper")
    print("Found movies:", len(movies))

    if not movies:
        raise Exception("can not found any movies in IMDb page. Selector is not working")

    titles = []
    links = []

    for movie in movies[:10]:
        title = movie.get_text(strip=True)
        href = movie['href']
        link = "https://www.imdb.com" + href.split('?')[0]
        titles.append(title)
        links.append(link)

    return list(zip(titles, links))


def get_summary_and_storyline(title):
    ia = Cinemagoer()
    movies = ia.search_movie(title)

    if not movies:
        return "No summary found.", "No storyline found."

    movie = ia.get_movie(movies[0].movieID)


    summary = movie.get('plot outline') or "No summary found."

    plot_list = movie.get('plot')
    storyline = plot_list[0].split('::')[0] if plot_list else "No storyline found."

    return summary, storyline


if __name__ == "__main__":
    print("\n--- FETCHING TOP 10 MOVIES ---")
    top_movies = get_top_10_movies()
    for i, (title, url) in enumerate(top_movies, start=1):
        print(f"{i}. {title} -> {url}")

    print("\n--- TESTING SUMMARY & STORYLINE (MOVIE #8) ---")
    raw_title = top_movies[1][0]
    clean_title = raw_title.split(". ", 1)[-1] if raw_title[1] == '.' else raw_title
    summary, storyline = get_summary_and_storyline(clean_title)

    print(f"\nSELECTED: {clean_title}")
    print("SUMMARY:", summary)
    print("STORYLINE:", storyline)
