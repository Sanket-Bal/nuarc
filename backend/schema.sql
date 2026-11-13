-- Anime Recommendation System: MySQL schema (MySQL 8.0.16+)
CREATE DATABASE IF NOT EXISTS anime_recommender
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE anime_recommender;

-- 1. Anime catalogue (loaded from the dataset)
CREATE TABLE anime (
    anime_id   INT PRIMARY KEY,              -- same id as the dataset
    title      VARCHAR(255) NOT NULL,
    synopsis   TEXT,
    type       VARCHAR(20),                  -- TV, Movie, OVA ...
    episodes   INT,
    score      DECIMAL(4,2),                 -- average community score
    members    INT,                          -- popularity (users who added it)
    INDEX idx_title (title)
);

-- 2. Genres (each genre stored once)
CREATE TABLE genres (
    genre_id   INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50) NOT NULL UNIQUE
);

-- 3. Anime <-> Genre (many-to-many link table)
CREATE TABLE anime_genres (
    anime_id   INT NOT NULL,
    genre_id   INT NOT NULL,
    PRIMARY KEY (anime_id, genre_id),
    FOREIGN KEY (anime_id) REFERENCES anime(anime_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES genres(genre_id) ON DELETE CASCADE
);

-- 4. Users
CREATE TABLE users (
    user_id    INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. Questionnaire answers (e.g. question_key = 'mood', answer = 'funny')
CREATE TABLE questionnaire_answers (
    answer_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    question_key VARCHAR(50) NOT NULL,
    answer       VARCHAR(255) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 6a. Movies (loaded from the TMDB dataset)
CREATE TABLE movies (
    movie_id      INT PRIMARY KEY,           -- same id as the dataset
    title         VARCHAR(255) NOT NULL,
    release_year  SMALLINT,
    overview      TEXT,                      -- plot summary
    keywords      TEXT,                      -- theme tags, comma separated
    vote_average  DECIMAL(4,2),
    vote_count    INT,
    INDEX idx_movie_title (title)
);

-- 6b. Movie genres and the movie <-> genre link table
CREATE TABLE movie_genres (
    genre_id   INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(50) NOT NULL UNIQUE
);
CREATE TABLE movie_genre_links (
    movie_id   INT NOT NULL,
    genre_id   INT NOT NULL,
    PRIMARY KEY (movie_id, genre_id),
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES movie_genres(genre_id) ON DELETE CASCADE
);

-- 6c. Favourite movies chosen by the user
CREATE TABLE favourite_movies (
    fav_id     INT AUTO_INCREMENT PRIMARY KEY,
    user_id    INT NOT NULL,
    movie_id   INT NOT NULL,
    UNIQUE (user_id, movie_id),
    FOREIGN KEY (user_id)  REFERENCES users(user_id)   ON DELETE CASCADE,
    FOREIGN KEY (movie_id) REFERENCES movies(movie_id) ON DELETE CASCADE
);

-- 7. Finished anime with the user's rating
CREATE TABLE watch_history (
    watch_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id     INT NOT NULL,
    anime_id    INT NOT NULL,
    rating      TINYINT NOT NULL,
    finished_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_rating CHECK (rating BETWEEN 1 AND 10),
    UNIQUE (user_id, anime_id),              -- one rating per anime per user
    FOREIGN KEY (user_id)  REFERENCES users(user_id)  ON DELETE CASCADE,
    FOREIGN KEY (anime_id) REFERENCES anime(anime_id) ON DELETE CASCADE
);

-- 8. Recommendations shown to users
CREATE TABLE recommendations (
    rec_id       INT AUTO_INCREMENT PRIMARY KEY,
    user_id      INT NOT NULL,
    anime_id     INT NOT NULL,
    similarity   DECIMAL(6,4) NOT NULL,      -- cosine similarity score
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)  REFERENCES users(user_id)  ON DELETE CASCADE,
    FOREIGN KEY (anime_id) REFERENCES anime(anime_id) ON DELETE CASCADE
);
