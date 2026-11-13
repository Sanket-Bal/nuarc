"""Anime Recommender for newcomers - command-line app.

Run:  python app.py
Needs: pip install pandas scikit-learn mysql-connector-python
Files needed in the same folder: app.py, recommender.py, load_data.py
"""
import getpass
import os

import mysql.connector

from load_data import DB_CONFIG
from recommender import AnimeModel, load_anime_from_db

GENRE_CHOICES = ["Action", "Adventure", "Comedy", "Drama", "Fantasy", "Horror",
                 "Mystery", "Romance", "Sci-Fi", "Slice of Life", "Sports",
                 "Supernatural", "Suspense"]
MOODS = {                       # mood -> extra anime genres added to the taste
    "Funny and light": ["Comedy", "Slice of Life"],
    "Emotional": ["Drama", "Romance"],
    "Thrilling": ["Action", "Suspense"],
    "Dark and mysterious": ["Mystery", "Horror", "Supernatural"],
    "Epic adventure": ["Adventure", "Fantasy"],
}
LENGTHS = {                     # length answer -> which anime to search
    "Short (up to 13 episodes)":  {"types": ("TV",), "min_episodes": 2, "max_episodes": 13},
    "Medium (up to 26 episodes)": {"types": ("TV",), "min_episodes": 2, "max_episodes": 26},
    "Long (any length)":          {"types": ("TV",), "min_episodes": 2, "max_episodes": None},
    "A movie (one sitting)":      {"types": ("Movie",), "min_episodes": None, "max_episodes": None},
}
DEFAULT_LENGTH = "Long (any length)"


# ---------- small input helpers ----------
def ask_number(prompt, low, high):
    while True:
        text = input(prompt).strip()
        if text.isdigit() and low <= int(text) <= high:
            return int(text)
        print(f"  Please enter a number from {low} to {high}.")


def ask_many(prompt, options):
    """Comma separated numbers, e.g. 1,3,5 -> list of chosen options."""
    while True:
        try:
            picks = sorted({int(x) for x in input(prompt).replace(" ", "").split(",") if x})
        except ValueError:
            picks = []
        if picks and all(1 <= p <= len(options) for p in picks):
            return [options[p - 1] for p in picks]
        print("  Enter numbers separated by commas, like 1,3,5.")


def show_options(options):
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")


# ---------- users ----------
def get_or_create_user(conn, cur, username):
    cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    rows = cur.fetchall()
    if rows:
        return rows[0][0], False
    cur.execute("INSERT INTO users (username) VALUES (%s)", (username,))
    conn.commit()
    return cur.lastrowid, True


# ---------- questionnaire ----------
def search_movies(cur, text):
    cur.execute("SELECT movie_id, title, release_year FROM movies "
                "WHERE title LIKE %s ORDER BY vote_count DESC LIMIT 8",
                (f"%{text.replace('%', '')}%",))
    return cur.fetchall()


def pick_movies(cur):
    chosen = []                                   # list of (movie_id, title)
    print("\n4) Name up to 3 favourite movies (type part of a title, Enter to stop).")
    while len(chosen) < 3:
        text = input(f"  Movie {len(chosen) + 1}: ").strip()
        if not text:
            break
        results = search_movies(cur, text)
        if not results:
            print("  No match found, try another spelling.")
            continue
        for i, (_, title, year) in enumerate(results, 1):
            print(f"    {i}. {title} ({year})")
        n = ask_number("  Pick a number (0 = none of these): ", 0, len(results))
        if n and results[n - 1][0] not in [c[0] for c in chosen]:
            chosen.append((results[n - 1][0], results[n - 1][1]))
            print(f"  Added: {results[n - 1][1]}")
    return chosen


def run_questionnaire(conn, cur, user_id):
    print("\n--- Tell us your taste ---")
    print("\n1) Which genres do you enjoy? (choose several)")
    show_options(GENRE_CHOICES)
    genres = ask_many("  Your genres (e.g. 1,5,9): ", GENRE_CHOICES)

    print("\n2) What mood are you in?")
    mood_names = list(MOODS)
    show_options(mood_names)
    mood = mood_names[ask_number("  Your mood: ", 1, len(mood_names)) - 1]

    print("\n3) How long should the anime be?")
    length_names = list(LENGTHS)
    show_options(length_names)
    length = length_names[ask_number("  Your choice: ", 1, len(length_names)) - 1]

    movies = pick_movies(cur)

    cur.execute("DELETE FROM questionnaire_answers WHERE user_id = %s", (user_id,))
    cur.execute("DELETE FROM favourite_movies WHERE user_id = %s", (user_id,))
    cur.executemany(
        "INSERT INTO questionnaire_answers (user_id, question_key, answer) VALUES (%s, %s, %s)",
        [(user_id, "genres", ", ".join(genres)), (user_id, "mood", mood),
         (user_id, "length", length)])
    cur.executemany("INSERT INTO favourite_movies (user_id, movie_id) VALUES (%s, %s)",
                    [(user_id, movie_id) for movie_id, _ in movies])
    conn.commit()


# ---------- taste profile (rebuilt from the database every time) ----------
def load_taste(cur, user_id):
    cur.execute("SELECT question_key, answer FROM questionnaire_answers WHERE user_id = %s",
                (user_id,))
    answers = dict(cur.fetchall())
    if "genres" not in answers:
        return None
    picked = answers["genres"].split(", ")
    # the genres the user picked count double; the mood only adds a little extra
    genres = picked + picked + [g for g in MOODS.get(answers.get("mood"), []) if g not in picked]

    cur.execute("""
        SELECT m.movie_id, m.title, m.overview, m.keywords,
               GROUP_CONCAT(mg.name SEPARATOR ', ')
        FROM favourite_movies f
        JOIN movies m ON m.movie_id = f.movie_id
        LEFT JOIN movie_genre_links l ON l.movie_id = m.movie_id
        LEFT JOIN movie_genres mg ON mg.genre_id = l.genre_id
        WHERE f.user_id = %s
        GROUP BY m.movie_id, m.title, m.overview, m.keywords""", (user_id,))
    movies = [{"title": t, "overview": o, "keywords": k, "genres": (g or "").split(", ")}
              for _, t, o, k, g in cur.fetchall()]
    return {"genres": genres, "movies": movies,
            "length_rule": LENGTHS.get(answers.get("length"), LENGTHS[DEFAULT_LENGTH])}


def build_profile(model, cur, user_id, taste):
    profile = model.starting_profile(taste["genres"], taste["movies"])
    cur.execute("SELECT anime_id, rating FROM watch_history WHERE user_id = %s ORDER BY watch_id",
                (user_id,))
    watched = cur.fetchall()
    for anime_id, rating in watched:
        if anime_id in model.row_of:
            profile = model.update_profile(profile, anime_id, rating)
    return profile, [anime_id for anime_id, _ in watched]


# ---------- menu actions ----------
def show_recommendations(model, conn, cur, user_id, taste):
    profile, watched_ids = build_profile(model, cur, user_id, taste)
    recs = model.recommend(profile, watched_ids=watched_ids, n=5, **taste["length_rule"])
    if recs.empty:
        print("\nNo matches found. Try updating your tastes (option 3).")
        return recs
    cur.executemany(
        "INSERT INTO recommendations (user_id, anime_id, similarity) VALUES (%s, %s, %s)",
        [(user_id, int(r.anime_id), round(float(r.similarity), 4))
         for r in recs.itertuples()])
    conn.commit()
    print("\n=== Recommended for you ===")
    for i, r in enumerate(recs.itertuples(), 1):
        episodes = "?" if r.episodes != r.episodes else int(r.episodes)   # NaN check
        print(f"{i}. {r.title}  [{r.type}, {episodes} ep, score {r.score}]")
        print(f"   {r.genres}")
    return recs


def finish_anime(model, conn, cur, user_id, last_recs):
    print("\nWhich anime did you finish?")
    options = [] if last_recs is None else list(zip(last_recs["anime_id"], last_recs["title"]))
    for i, (_, title) in enumerate(options, 1):
        print(f"  {i}. {title}")
    print("  0. Another anime (search by title)")
    n = ask_number("  Your choice: ", 0, len(options))
    if n:
        anime_id, title = int(options[n - 1][0]), options[n - 1][1]
    else:
        text = input("  Part of the anime title: ").strip().replace("%", "")
        cur.execute("SELECT anime_id, title, type FROM anime WHERE title LIKE %s "
                    "ORDER BY members DESC LIMIT 8", (f"%{text}%",))
        results = [r for r in cur.fetchall() if r[0] in model.row_of]
        if not results:
            print("  No match found.")
            return False
        for i, (_, t, kind) in enumerate(results, 1):
            print(f"    {i}. {t} [{kind}]")
        pick = ask_number("  Pick a number (0 = cancel): ", 0, len(results))
        if not pick:
            return False
        anime_id, title = int(results[pick - 1][0]), results[pick - 1][1]

    rating = ask_number(f"  Your rating for '{title}' (1-10): ", 1, 10)
    cur.execute("INSERT INTO watch_history (user_id, anime_id, rating) VALUES (%s, %s, %s) "
                "ON DUPLICATE KEY UPDATE rating = VALUES(rating), finished_at = CURRENT_TIMESTAMP",
                (user_id, anime_id, rating))
    conn.commit()
    if rating <= 5:
        print("  Saved. We won't recommend it again, and it won't pull your taste towards it.")
    else:
        print("  Saved. Your taste profile has learned from it!")
    return True


def show_history(cur, user_id):
    cur.execute("SELECT a.title, w.rating, DATE(w.finished_at) FROM watch_history w "
                "JOIN anime a ON a.anime_id = w.anime_id WHERE w.user_id = %s "
                "ORDER BY w.watch_id", (user_id,))
    rows = cur.fetchall()
    print("\n=== Your finished anime ===")
    if not rows:
        print("  Nothing yet.")
    for title, rating, day in rows:
        print(f"  {title} - rated {rating}/10 ({day})")


# ---------- main ----------
def main():
    password = os.environ.get("ANIME_DB_PASSWORD") or getpass.getpass("MySQL root password: ")
    conn = mysql.connector.connect(password=password, **DB_CONFIG)
    cur = conn.cursor()
    print("Loading anime data and building the model (about 10 seconds)...")
    model = AnimeModel(load_anime_from_db(conn))

    print("\n=== Anime Recommender for newcomers ===")
    username = ""
    while not username:
        username = input("Enter your username: ").strip()[:50]
    user_id, is_new = get_or_create_user(conn, cur, username)

    taste = load_taste(cur, user_id)
    if taste is None:
        print(f"Welcome, {username}! Let's find out what you like.")
        run_questionnaire(conn, cur, user_id)
        taste = load_taste(cur, user_id)
    else:
        print(f"Welcome back, {username}!")
    last_recs = show_recommendations(model, conn, cur, user_id, taste)

    while True:
        print("\n--- Menu ---")
        print("  1. Show recommendations again")
        print("  2. I finished an anime (rate it)")
        print("  3. Update my tastes (redo the questions)")
        print("  4. My finished anime")
        print("  5. Quit")
        choice = ask_number("Your choice: ", 1, 5)
        if choice == 1:
            last_recs = show_recommendations(model, conn, cur, user_id, taste)
        elif choice == 2:
            if finish_anime(model, conn, cur, user_id, last_recs):
                last_recs = show_recommendations(model, conn, cur, user_id, taste)
        elif choice == 3:
            run_questionnaire(conn, cur, user_id)
            taste = load_taste(cur, user_id)
            last_recs = show_recommendations(model, conn, cur, user_id, taste)
        elif choice == 4:
            show_history(cur, user_id)
        else:
            break
    print("Enjoy your anime! Goodbye.")
    cur.close()
    conn.close()


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
