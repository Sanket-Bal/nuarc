-- Movie tables for the anime recommender (run once on your existing database)
USE anime_recommender;

-- 1. Movies (loaded from the TMDB dataset)
CREATE TABLE IF NOT EXISTS movies (
    movie_id      INT PRIMARY KEY,           -- same id as the dataset
    title         VARCHAR(255) NOT NULL,
    release_year  SMALLINT,
    overview      TEXT,                      -- plot summary
    keywords      TEXT,                      -- theme tags, comma separated
    vote_average  DECIMAL(4,2),
    vote_count    INT,
    INDEX idx_movie_title (title)
);

-- 2. Movie genres (each stored once)
CREATE TABLE IF NOT EXISTS movie_genres (
    genre_id   INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50) NOT NULL UNIQUE
);

-- 3. Movie <-> Genre link table
CREATE TABLE IF NOT EXISTS movie_genre_links (
    movie_id   INT NOT NULL,
    genre_id   INT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES movie_genres(genre_id) ON DELETE CASCADE
);

-- 4. favourite_movies now points to the movies table.
--    It is still empty, so we can safely rebuild it.
DROP TABLE IF EXISTS favourite_movies;
CREATE TABLE favourite_movies (
    fav_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    movie_id   INT NOT NULL,
    UNIQUE (user_id, movie_id),
    FOREIGN KEY (user_id)  REFERENCES users(user_id)   ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);
