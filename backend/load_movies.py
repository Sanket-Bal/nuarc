"""Load the TMDB 5000 movies CSV into the movie tables of anime_recommender.

Run:  python load_movies.py
Needs: pip install pandas mysql-connector-python
(Run movie_schema.sql in Workbench first.)
"""
import getpass
import json
import os

import mysql.connector
import pandas as pd

from load_data import DB_CONFIG

# ---------- settings ----------
CSV_PATH = "tmdb_5000_movies.csv"
ONLY_ENGLISH = True          # Hollywood-focused: keep original_language == 'en'


def names_from_json(text):
    """'[{"id": 28, "name": "Action"}, ...]' -> ['Action', ...]"""
    if pd.isna(text):
        return []
    try:
        return [item["name"].strip() for item in json.loads(text) if item.get("name")]
    except (ValueError, TypeError):
        return []


def number_or_none(value, as_int=False):
    number = pd.to_numeric(value, errors="coerce")
    if pd.isna(number):
        return None
    return int(number) if as_int else float(number)


def build_movie_rows(df):
    """Clean the CSV. Returns (movie_rows, links) where links = (movie_id, genre_name)."""
    movie_rows, links = [], []
    for _, row in df.iterrows():
        if ONLY_ENGLISH and row["original_language"] != "en":
            continue
        if row["status"] != "Released":
            continue
        overview = row["overview"]
        genres = names_from_json(row["genres"])
        if pd.isna(overview) or not str(overview).strip() or not genres:
            continue                          # no plot text or no genre: not useful

        movie_id = int(row["id"])
        year = pd.to_datetime(row["release_date"], errors="coerce").year
        keywords = ", ".join(names_from_json(row["keywords"]))
        movie_rows.append((
            movie_id,
            str(row["title"]).strip()[:255],
            None if pd.isna(year) else int(year),
            str(overview).strip(),
            keywords or None,
            number_or_none(row["vote_average"]),
            number_or_none(row["vote_count"], as_int=True),
        ))
        links.extend((movie_id, g) for g in genres)
    return movie_rows, links


def main():
    df = pd.read_csv(CSV_PATH)
    movie_rows, links = build_movie_rows(df)
    print(f"Kept {len(movie_rows)} of {len(df)} movies.")

    password = os.environ.get("ANIME_DB_PASSWORD") or getpass.getpass("MySQL root password: ")
    conn = mysql.connector.connect(password=password, **DB_CONFIG)
    cur = conn.cursor()

    # 1. movies (re-running updates existing rows)
    cur.executemany(
        "INSERT INTO movies (movie_id, title, release_year, overview, keywords, "
        "vote_average, vote_count) VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE title=VALUES(title), release_year=VALUES(release_year), "
        "overview=VALUES(overview), keywords=VALUES(keywords), "
        "vote_average=VALUES(vote_average), vote_count=VALUES(vote_count)", movie_rows)

    # 2. genres
    genre_names = sorted({name for _, name in links})
    cur.executemany("INSERT IGNORE INTO movie_genres (name) VALUES (%s)",
                    [(g,) for g in genre_names])
    cur.execute("SELECT genre_id, name FROM movie_genres")
    genre_id = {name: gid for gid, name in cur.fetchall()}

    # 3. movie_genre_links
    cur.executemany(
        "INSERT IGNORE INTO movie_genre_links (movie_id, genre_id) VALUES (%s, %s)",
        [(mid, genre_id[name]) for mid, name in links])

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done: {len(movie_rows)} movies, {len(genre_names)} genres, {len(links)} links.")


if __name__ == "__main__":
    main()
