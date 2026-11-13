"""Anime recommender engine: TF-IDF + cosine similarity, with a taste profile
that learns from the ratings of finished anime.

Run a demo:  python recommender.py
Needs: pip install pandas scikit-learn mysql-connector-python
"""
import getpass
import os
import re

import mysql.connector
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

from load_data import DB_CONFIG

GENRE_WEIGHT = 3        # genres are repeated so they matter more than synopsis words
LEARN_RATE = 0.4        # max share a finished anime can take in the profile (rating 10)


# ---------- 1. get data from MySQL ----------
def load_anime_from_db(conn=None):
    """Read all anime (with their genres) from MySQL into a pandas table."""
    own_connection = conn is None
    if own_connection:
        password = os.environ.get("ANIME_DB_PASSWORD") or getpass.getpass("MySQL root password: ")
        conn = mysql.connector.connect(password=password, **DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT a.anime_id, a.title, a.synopsis, a.type, a.episodes, a.score, a.members,
               GROUP_CONCAT(g.name SEPARATOR ', ') AS genres
        FROM anime a
        LEFT JOIN anime_genres ag ON ag.anime_id = a.anime_id
        LEFT JOIN genres g ON g.genre_id = ag.genre_id
        GROUP BY a.anime_id, a.title, a.synopsis, a.type, a.episodes, a.score, a.members
    """)
    columns = ["anime_id", "title", "synopsis", "type", "episodes", "score", "members", "genres"]
    df = pd.DataFrame(cur.fetchall(), columns=columns)
    cur.close()
    if own_connection:
        conn.close()
    df["score"] = pd.to_numeric(df["score"])          # DECIMAL -> float
    df["members"] = pd.to_numeric(df["members"])
    return df


# ---------- 2. the model ----------
# Movie genres (TMDB) -> anime genres (MyAnimeList). Genres with no match add nothing.
MOVIE_TO_ANIME_GENRES = {
    "Action": ["Action"], "Adventure": ["Adventure"], "Fantasy": ["Fantasy"],
    "Science Fiction": ["Sci-Fi"], "Comedy": ["Comedy"], "Drama": ["Drama"],
    "Romance": ["Romance"], "Horror": ["Horror"], "Mystery": ["Mystery"],
    "Thriller": ["Suspense"], "Crime": ["Mystery", "Suspense"],
    "War": ["Action", "Drama"], "History": ["Drama"], "Western": ["Action", "Adventure"],
    "Family": [], "Animation": [], "Music": [], "Documentary": [],
    "TV Movie": [], "Foreign": [],
}

# TMDB (movie) genre -> MyAnimeList (anime) genres. Genres with no match add nothing.
MOVIE_TO_ANIME_GENRES = {
    "Action": ["Action"], "Adventure": ["Adventure"], "Comedy": ["Comedy"],
    "Drama": ["Drama"], "Fantasy": ["Fantasy"], "Horror": ["Horror"],
    "Mystery": ["Mystery"], "Romance": ["Romance"], "Science Fiction": ["Sci-Fi"],
    "Thriller": ["Suspense"], "Crime": ["Mystery", "Suspense"],
    "War": ["Action", "Drama"], "History": ["Drama"], "Western": ["Action", "Adventure"],
    "Family": [], "Animation": [], "Music": [], "Documentary": [],
    "TV Movie": [], "Foreign": [],
}


SEQUEL_PATTERN = re.compile(
    r"(\b\d+(st|nd|rd|th) season\b|\bseason \d+\b|\bmovie [2-9]\b|\bpart [2-9]\b"
    r"|\bfinal season\b|\bmovie\b|\brecap|\b(II|III|IV|VI|VII|VIII)\b|\s[2-9]$)", re.IGNORECASE)


def looks_like_sequel(title):
    """Rough guess from the title: sequels, spin-off movies, recaps. Not perfect."""
    return bool(SEQUEL_PATTERN.search(title))

def genre_tokens(genres):
    """['Sci-Fi', 'Slice of Life'] -> 'sci_fi slice_of_life' (one token per genre)."""
    return " ".join(g.lower().replace("-", "_").replace(" ", "_") for g in genres)


class AnimeModel:
    def __init__(self, anime_df):
        self.df = anime_df.reset_index(drop=True)
        genre_lists = self.df["genres"].fillna("").apply(
            lambda s: [g.strip() for g in s.split(",") if g.strip()])
        text = (genre_lists.apply(genre_tokens) + " ") * GENRE_WEIGHT \
            + self.df["synopsis"].fillna("")
        self.vectorizer = TfidfVectorizer(stop_words="english", min_df=2,
                                          max_features=30000)
        self.matrix = self.vectorizer.fit_transform(text)     # rows are L2-normalised
        self.row_of = {aid: i for i, aid in enumerate(self.df["anime_id"])}
        self.df["is_sequel"] = self.df["title"].apply(looks_like_sequel)
        # popularity percentile (0 = least watched, 1 = most watched)
        self.df["popularity"] = self.df["members"].fillna(0).rank(pct=True)

    # --- build a starting taste profile from the questionnaire ---
    def make_profile(self, genres, free_text=""):
        """genres: list of genre names; free_text: words about stories/movies they like."""
        text = (genre_tokens(genres) + " ") * GENRE_WEIGHT + free_text
        return normalize(self.vectorizer.transform([text]))

    # --- a favourite movie -> a vector in the anime space ---
    def movie_vector(self, movie_genres, overview, keywords=""):
        """Movie genres are mapped to anime genres; plot overview + keywords add the themes."""
        anime_genres = []
        for g in movie_genres:
            for a in MOVIE_TO_ANIME_GENRES.get(g, []):
                if a not in anime_genres:
                    anime_genres.append(a)
        text = (genre_tokens(anime_genres) + " ") * GENRE_WEIGHT \
            + f" {overview or ''} {keywords or ''}"
        return normalize(self.vectorizer.transform([text]))

    def starting_profile(self, genres, movies):
        """Questionnaire genres and favourite movies share the starting taste equally.
        movies: list of dicts with keys genres (list), overview, keywords."""
        parts = []
        if genres:
            parts.append(self.make_profile(genres))
        if movies:
            vectors = [self.movie_vector(m["genres"], m["overview"], m["keywords"])
                       for m in movies]
            parts.append(normalize(sum(vectors)))
        if not parts:
            return None
        return normalize(sum(parts))

    # --- build a profile from favourite movies ---
    def movie_vector(self, genres, overview="", keywords=""):
        """One movie -> a vector in the same space as the anime."""
        anime_genres = sorted({a for g in genres for a in MOVIE_TO_ANIME_GENRES.get(g, [])})
        text = (genre_tokens(anime_genres) + " ") * GENRE_WEIGHT \
            + (keywords or "") + " " + (overview or "")
        return normalize(self.vectorizer.transform([text]))

    def make_profile_from_movies(self, movies):
        """movies: list of dicts with keys genres (list), overview, keywords."""
        vectors = [self.movie_vector(m["genres"], m.get("overview", ""), m.get("keywords", ""))
                   for m in movies]
        return normalize(sum(vectors))

    @staticmethod
    def combine_profiles(profiles, weights):
        """Weighted mix, e.g. questionnaire 0.5 + movies 0.5."""
        return normalize(sum(w * p for p, w in zip(profiles, weights)))

    # --- learn from a finished anime ---
    def update_profile(self, profile, anime_id, rating):
        """Blend the finished anime into the profile. Rating <= 5 adds nothing."""
        weight = max(0.0, (rating - 5) / 5) * LEARN_RATE     # 10 -> 0.4, 8 -> 0.24, 6 -> 0.08
        anime_vec = self.matrix[self.row_of[anime_id]]
        return normalize((1 - weight) * profile + weight * anime_vec)

    # --- recommend ---
    def recommend(self, profile, watched_ids=(), n=5, min_score=6.5, min_members=50000,
                  max_episodes=None, min_episodes=None, types=("TV", "Movie"),
                  include_sequels=False):
        sims = cosine_similarity(profile, self.matrix).ravel()
        keep = self.df["score"].fillna(0) >= min_score          # newcomers: well-rated shows
        keep &= self.df["members"].fillna(0) >= min_members     # ... that many people watched
        keep &= self.df["type"].isin(types)
        keep &= ~self.df["anime_id"].isin(watched_ids)
        if not include_sequels:
            keep &= ~self.df["is_sequel"]
        episodes = self.df["episodes"]
        if min_episodes:                       # unknown count = still running, so allowed
            keep &= episodes.isna() | (episodes >= min_episodes)
        if max_episodes is not None:           # unknown counts are left out here
            keep &= episodes.between(1, max_episodes)
        result = self.df.assign(similarity=sims)[keep.values]
        # final rank: similarity, boosted a little for well-known anime (weight 0.6 to 1.0)
        result = result.assign(rank_value=result["similarity"] * (0.6 + 0.4 * result["popularity"]))
        result = result.sort_values("rank_value", ascending=False)
        return result.drop(columns="rank_value").head(n)


# ---------- 3. demo ----------
if __name__ == "__main__":
    model = AnimeModel(load_anime_from_db())
    cols = ["title", "genres", "score", "similarity"]

    profile = model.make_profile(["Action", "Fantasy"], "friendship, a journey, magic")
    first = model.recommend(profile, max_episodes=30)
    print("\nFirst recommendations:\n", first[cols].to_string(index=False))

    # pretend the user finished the top result and rated it 9/10
    finished_id = int(first.iloc[0]["anime_id"])
    profile = model.update_profile(profile, finished_id, rating=9)
    second = model.recommend(profile, watched_ids=[finished_id], max_episodes=30)
    print(f"\nAfter finishing '{first.iloc[0]['title']}' (rated 9):\n",
          second[cols].to_string(index=False))
