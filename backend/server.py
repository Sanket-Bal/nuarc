"""FastAPI server for Anime Recommender with Supabase auth."""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client, Client

from auth_utils import get_current_user

# Supabase client
supabase: Client = None
model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize Supabase client and model on startup."""
    global supabase, model
    
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env file")
    
    supabase = create_client(supabase_url, supabase_key)
    print("✅ Supabase client initialized")
    print("Loading anime data and building the model...")
    # TODO: Load anime data from Supabase or CSV
    # model = AnimeModel(load_anime_from_db(supabase))
    
    yield
    # Cleanup if needed


app = FastAPI(
    title="Anime Recommender API",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TasteUpdate(BaseModel):
    genres: list[str]
    mood: str
    length: str


class AnimeRating(BaseModel):
    anime_id: int
    rating: int


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


@app.get("/users/me")
def get_current_user_profile(user_id: str = Depends(get_current_user)):
    """Get current user's profile."""
    try:
        response = supabase.table("profiles").select("*").eq("id", user_id).single().execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Profile not found")


@app.get("/users/me/taste")
def get_taste(user_id: str = Depends(get_current_user)):
    """Get user's taste preferences."""
    try:
        response = supabase.table("taste_preferences").select("*").eq("user_id", user_id).single().execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=404, detail="Taste preferences not found")


@app.post("/users/me/taste")
def update_taste(taste: TasteUpdate, user_id: str = Depends(get_current_user)):
    """Update user's taste preferences."""
    try:
        data = {
            "user_id": user_id,
            "genres": taste.genres,
            "mood": taste.mood,
            "length": taste.length,
        }
        supabase.table("taste_preferences").upsert(data).execute()
        return {"status": "updated"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/me/recommendations")
def get_recommendations(user_id: str = Depends(get_current_user)):
    """Get anime recommendations for user."""
    if not model:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # TODO: Implement recommendation logic with Supabase
        return {"recommendations": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/users/me/watch-history")
def rate_anime(rating: AnimeRating, user_id: str = Depends(get_current_user)):
    """Rate a finished anime."""
    try:
        data = {
            "user_id": user_id,
            "anime_id": rating.anime_id,
            "rating": rating.rating,
        }
        supabase.table("watch_history").upsert(data).execute()
        return {"status": "saved"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/users/me/watch-history")
def get_watch_history(user_id: str = Depends(get_current_user)):
    """Get user's watch history."""
    try:
        response = supabase.table("watch_history").select("*").eq("user_id", user_id).execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
