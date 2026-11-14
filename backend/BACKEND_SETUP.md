# FastAPI Backend Setup with Supabase

## Step 1: Get Supabase Credentials

1. Go to your Supabase project dashboard
2. Click **Settings** → **API**
3. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **Service Role Key** → `SUPABASE_SERVICE_ROLE_KEY` (⚠️ Keep secret!)
   - **JWT Secret** → `SUPABASE_JWT_SECRET` (⚠️ Keep secret!)

## Step 2: Set Up Environment Variables

1. Create `.env` file in `backend/` directory:
```
SUPABASE_URL=https://hwixuqzugmerhuteleax.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here
SUPABASE_JWT_SECRET=your_jwt_secret_here
```

⚠️ **Never commit `.env` to GitHub!** It's already in `.gitignore`

## Step 3: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## Step 4: Run the Server

```bash
uvicorn server:app --reload
```

Server runs at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

## How It Works

### Frontend → Backend Flow

1. **User signs in** on frontend
2. Supabase creates session with JWT token
3. Frontend calls API with `Authorization: Bearer <token>`
4. FastAPI verifies token using `SUPABASE_JWT_SECRET`
5. If valid, extracts `user_id` from token
6. Endpoint executes with user context

### Example Request

```javascript
// Frontend
const response = await fetch('http://localhost:8000/users/me/taste', {
  headers: {
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiI...',
    'Content-Type': 'application/json',
  }
})
```

```python
# Backend
@app.get("/users/me/taste")
def get_taste(user_id: str = Depends(get_current_user)):
    # user_id is automatically extracted from token
    # RLS policies ensure user can only access their own data
    return supabase.table("taste_preferences").select("*").eq("user_id", user_id).execute()
```

## Protected Endpoints

All endpoints require valid Supabase JWT token:

- `GET /users/me` - Get current user profile
- `GET /users/me/taste` - Get taste preferences
- `POST /users/me/taste` - Update taste preferences
- `GET /users/me/recommendations` - Get recommendations
- `POST /users/me/watch-history` - Rate anime
- `GET /users/me/watch-history` - Get watch history

## Security

- ✅ JWT tokens verified on every request
- ✅ User ID extracted from token (can't be spoofed)
- ✅ Supabase RLS policies enforce data isolation
- ✅ Service role key never exposed to frontend
- ✅ CORS configured for frontend only

## Troubleshooting

**"Missing SUPABASE_URL"** - Check `.env` file exists and has correct values

**"Invalid token"** - Token expired or wrong JWT secret

**"CORS error"** - Make sure frontend URL is in CORS allowed origins

**"Profile not found"** - User hasn't confirmed email yet

## Files

- `server.py` - Main FastAPI application
- `supabase_auth.py` - JWT verification logic
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create from `.env.example`)
