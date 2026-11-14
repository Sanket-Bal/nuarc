-- Profiles table (already created, adding update/delete policies)
create policy "Users can update own profile"
on profiles for update
using (auth.uid() = id)
with check (auth.uid() = id);

create policy "Users can delete own profile"
on profiles for delete
using (auth.uid() = id);

-- Taste preferences table
create table taste_preferences (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  genres text[] not null,
  mood text not null,
  length text not null,
  updated_at timestamp with time zone default now(),
  unique(user_id)
);

alter table taste_preferences enable row level security;

create policy "Users can view own taste"
on taste_preferences for select
using (auth.uid() = user_id);

create policy "Users can insert own taste"
on taste_preferences for insert
with check (auth.uid() = user_id);

create policy "Users can update own taste"
on taste_preferences for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can delete own taste"
on taste_preferences for delete
using (auth.uid() = user_id);

-- Favorite movies table
create table favourite_movies (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  movie_id integer not null,
  added_at timestamp with time zone default now()
);

alter table favourite_movies enable row level security;

create policy "Users can view own favourite movies"
on favourite_movies for select
using (auth.uid() = user_id);

create policy "Users can insert own favourite movies"
on favourite_movies for insert
with check (auth.uid() = user_id);

create policy "Users can delete own favourite movies"
on favourite_movies for delete
using (auth.uid() = user_id);

-- Watch history table
create table watch_history (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  anime_id integer not null,
  rating integer not null check (rating >= 1 and rating <= 10),
  finished_at timestamp with time zone default now(),
  created_at timestamp with time zone default now()
);

alter table watch_history enable row level security;

create policy "Users can view own watch history"
on watch_history for select
using (auth.uid() = user_id);

create policy "Users can insert own watch history"
on watch_history for insert
with check (auth.uid() = user_id);

create policy "Users can update own watch history"
on watch_history for update
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users can delete own watch history"
on watch_history for delete
using (auth.uid() = user_id);

-- Recommendations table
create table recommendations (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references profiles(id) on delete cascade,
  anime_id integer not null,
  similarity numeric not null,
  created_at timestamp with time zone default now()
);

alter table recommendations enable row level security;

create policy "Users can view own recommendations"
on recommendations for select
using (auth.uid() = user_id);

create policy "Users can insert own recommendations"
on recommendations for insert
with check (auth.uid() = user_id);

-- Create indexes for better query performance
create index idx_taste_preferences_user_id on taste_preferences(user_id);
create index idx_favourite_movies_user_id on favourite_movies(user_id);
create index idx_watch_history_user_id on watch_history(user_id);
create index idx_recommendations_user_id on recommendations(user_id);
