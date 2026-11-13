"""Load an anime CSV (MyAnimeList style) into the anime_recommender MySQL database.

Run:  python load_data.py
Needs: pip install pandas mysql-connector-python
"""
import getpass

import mysql.connector
import pandas as pd

# ---------- settings (change if needed) ----------
CSV_PATH = "anime-dataset-2023.csv"   # path to your downloaded CSV
DB_CONFIG = {
    "host": "127.0.0.1",
    "port": 3306,
    "user": "root",
    "database": "anime_recommender",
}
EXCLUDE_ADULT = True                  # set False to keep adult titles
ADULT_GENRES = {"Hentai", "Erotica"}

# The script looks for these column names in your CSV (first match wins).
CANDIDATES = {
    "anime_id": ["anime_id", "MAL_ID", "id"],
    "title":    ["Name", "name", "title", "English name"],
    "synopsis": ["Synopsis", "synopsis", "sypnopsis"],
    "type":     ["Type", "type"],
    "episodes": ["Episodes", "episodes"],
    "score":    ["Score", "score", "rating"],
    "genres":   ["Genres", "genres", "genre"],
    "members":  ["Members", "members"],   # popularity: how many users added it
    "age_rating": ["Rating"],         # e.g. "Rx - Hentai", "PG-13 - Teens 13 or older"
}
MISSING_WORDS = {"UNKNOWN", "Unknown", "N/A", "None", ""}


def find_columns(df):
    """Map our field names to the real column names in the CSV."""
    found = {}
    for field, names in CANDIDATES.items():
        found[field] = next((n for n in names if n in df.columns), None)
    for needed in ("anime_id", "title", "genres"):
        if found[needed] is None:
            raise SystemExit(f"Could not find a column for '{needed}'. "
                             f"Your CSV columns are: {list(df.columns)}")
    return found


def clean_text(value):
    if pd.isna(value) or str(value).strip() in MISSING_WORDS:
        return None
    return str(value).strip()


def clean_number(value, as_int=False):
    number = pd.to_numeric(value, errors="coerce")
    if pd.isna(number):
        return None
    return int(number) if as_int else float(number)


def is_adult(age_rating, genre_names):
    """True if the anime is rated Rx or has an adult genre."""
    if age_rating and age_rating.startswith("Rx"):
        return True
    return bool(set(genre_names) & ADULT_GENRES)


def build_rows(df, cols):
    """Turn the CSV into clean rows. Returns (anime_rows, links, skipped_adult)."""
    def get(row, field):
        col = cols[field]
        return row[col] if col else None

    anime_rows, links = [], []          # links = (anime_id, genre_name)
    seen_ids, skipped_adult = set(), 0
    for _, row in df.iterrows():
        anime_id = clean_number(get(row, "anime_id"), as_int=True)
        title = clean_text(get(row, "title"))
        if anime_id is None or title is None or anime_id in seen_ids:
            continue

        genre_text = clean_text(get(row, "genres")) or ""
        genre_names = [g.strip() for g in genre_text.split(",") if g.strip()]

        if EXCLUDE_ADULT and is_adult(clean_text(get(row, "age_rating")), genre_names):
            skipped_adult += 1
            continue

        seen_ids.add(anime_id)
        anime_rows.append((
            anime_id,
            title[:255],
            clean_text(get(row, "synopsis")),
            clean_text(get(row, "type")),
            clean_number(get(row, "episodes"), as_int=True),
            clean_number(get(row, "score")),
            clean_number(get(row, "members"), as_int=True),
        ))
        links.extend((anime_id, name) for name in genre_names)
    return anime_rows, links, skipped_adult


def main():
    df = pd.read_csv(CSV_PATH)
    cols = find_columns(df)
    print("Columns used:", cols)

    anime_rows, links, skipped_adult = build_rows(df, cols)
    print(f"Skipped {skipped_adult} adult titles.")

    password = getpass.getpass("MySQL root password: ")
    conn = mysql.connector.connect(password=password, **DB_CONFIG)
    cur = conn.cursor()

    # 1. anime (re-running updates existing rows)
    cur.executemany(
        "INSERT INTO anime (anime_id, title, synopsis, type, episodes, score, members) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s) "
        "ON DUPLICATE KEY UPDATE title=VALUES(title), synopsis=VALUES(synopsis), "
        "type=VALUES(type), episodes=VALUES(episodes), score=VALUES(score), "
        "members=VALUES(members)", anime_rows)

    # 2. genres (each name once)
    genre_names = sorted({name for _, name in links})
    cur.executemany("INSERT IGNORE INTO genres (name) VALUES (%s)",
                    [(g,) for g in genre_names])
    cur.execute("SELECT genre_id, name FROM genres")
    genre_id = {name: gid for gid, name in cur.fetchall()}

    # 3. anime_genres (link table)
    cur.executemany(
        "INSERT IGNORE INTO anime_genres (anime_id, genre_id) VALUES (%s, %s)",
        [(aid, genre_id[name]) for aid, name in links])

    conn.commit()
    cur.close()
    conn.close()
    print(f"Done: {len(anime_rows)} anime, {len(genre_names)} genres, "
          f"{len(links)} anime-genre links.")


if __name__ == "__main__":
    main()