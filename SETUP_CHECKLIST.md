# Complete Setup Checklist

## Frontend Setup ✅

- [x] Supabase client created (`supabaseClient.js`)
- [x] AuthContext with sign up/in/out (`AuthContext.jsx`)
- [x] Auth UI updated (`Auth.jsx`)
- [x] App wrapped with AuthProvider (`main.jsx`)
- [x] Environment variables configured (`.env.local`)
- [x] API client created (`api.js`)
- [x] Dependencies added to `package.json`

## Backend Setup

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Create `.env` file with Supabase credentials
- [ ] Run server: `uvicorn server:app --reload`

## Supabase Database Setup

### 1. Create Profiles Table (if not exists)
```sql
create table if not exists profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique not null,
  email text unique not null,
  created_at timestamp with time zone default now()
);

alter table profiles enable row level security;
```

### 2. Add RLS Policies
```sql
create policy "Users can view own profile"
on profiles for select
to authenticated
using (auth.uid() = id);

create policy "Users can insert own profile"
on profiles for insert
to authenticated
with check (auth.uid() = id);

create policy "Users can update own profile"
on profiles for update
to authenticated
using (auth.uid() = id)
with check (auth.uid() = id);

create policy "Users can delete own profile"
on profiles for delete
to authenticated
using (auth.uid() = id);
```

### 3. Add Auto-Profile Creation Trigger
```sql
create function public.handle_new_user()
returns trigger as $$
begin
  insert into public.profiles (id, email, username)
  values (new.id, new.email, new.raw_user_meta_data->>'username');
  return new;
end;
$$ language plpgsql security definer;

create trigger on_auth_user_created
after insert on auth.users
for each row execute function public.handle_new_user();
```

### 4. Configure Auth Settings
- [ ] Go to **Authentication → URL Configuration**
- [ ] Set Site URL to `http://localhost:5173`
- [ ] Add Redirect URL: `http://localhost:5173`

### 5. (Optional) Disable Email Confirmation for Testing
- [ ] Go to **Authentication → Providers → Email**
- [ ] Toggle off "Confirm email" (for testing only)
- [ ] Re-enable before production

## Testing Flow

1. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   Opens at `http://localhost:5173`

2. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn server:app --reload
   ```
   Opens at `http://localhost:8000`

3. **Test Sign Up**
   - Click "Start Exploring"
   - Click "Sign Up"
   - Enter email, password, username
   - Check email for confirmation link
   - Click link to confirm

4. **Test Sign In**
   - Click "Sign In"
   - Enter email and password
   - Should redirect to dashboard

5. **Test API**
   - Go to `http://localhost:8000/docs`
   - Click "Authorize"
   - Paste your access token from browser console:
     ```javascript
     const { data } = await supabase.auth.getSession()
     console.log(data.session.access_token)
     ```
   - Try endpoints

## Security Checklist

- [x] Anon key in frontend (safe)
- [x] Service role key in backend only (safe)
- [x] `.env.local` in `.gitignore` (safe)
- [x] `.env` in backend `.gitignore` (safe)
- [x] JWT verification on all endpoints (safe)
- [x] RLS policies on all tables (safe)
- [x] CORS configured (safe)

## Environment Variables

### Frontend (`.env.local`)
```
VITE_SUPABASE_URL=https://hwixuqzugmerhuteleax.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiI...
VITE_API_URL=http://localhost:8000
```

### Backend (`.env`)
```
SUPABASE_URL=https://hwixuqzugmerhuteleax.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJIUzI1NiI...
SUPABASE_JWT_SECRET=your_jwt_secret_here
```

## Common Issues & Fixes

| Issue | Fix |
|-------|-----|
| "relation profiles already exists" | Table already created, skip that SQL |
| "Email rate limit exceeded" | Wait 42 seconds or use temp email |
| "Waiting for verification" | Click confirmation link in email |
| "Invalid token" | Token expired, sign in again |
| "CORS error" | Check frontend URL in CORS config |
| "Profile not found" | User hasn't confirmed email yet |

## Next Steps

1. ✅ Complete all checklist items
2. ✅ Test sign up/sign in flow
3. ✅ Test API endpoints
4. ⏭️ Add taste preferences UI
5. ⏭️ Add recommendations logic
6. ⏭️ Add watch history UI
