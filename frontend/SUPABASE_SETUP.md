# Supabase Authentication Setup Guide

## Step 1: Get Your Supabase Credentials

1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Create a new project or select existing one
3. Go to **Settings** → **API**
4. Copy:
   - **Project URL** (VITE_SUPABASE_URL)
   - **Anon Public Key** (VITE_SUPABASE_ANON_KEY)

## Step 2: Configure Environment Variables

1. Open `frontend/.env.local`
2. Replace with your credentials:
```
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key-here
```

## Step 3: Set Up Supabase Database

Run this SQL in your Supabase SQL Editor:

```sql
create table profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  username text unique not null,
  email text unique not null,
  created_at timestamp with time zone default now()
);

alter table profiles enable row level security;

create policy "Users can view own profile"
on profiles for select
using (auth.uid() = id);

create policy "Users can insert own profile"
on profiles for insert
with check (auth.uid() = id);

create policy "Users can update own profile"
on profiles for update
using (auth.uid() = id)
with check (auth.uid() = id);

create policy "Users can delete own profile"
on profiles for delete
using (auth.uid() = id);
```

## Step 4: Install Dependencies

```bash
cd frontend
npm install
```

## Step 5: Run the Development Server

```bash
npm run dev
```

## How It Works

### Sign Up Flow
1. User enters email, password, and username
2. `AuthContext.signUp()` creates auth user in Supabase
3. Profile is automatically created in `profiles` table
4. User receives confirmation email
5. After confirming email, user can sign in

### Sign In Flow
1. User enters email and password
2. `AuthContext.signIn()` authenticates with Supabase
3. Session token is stored automatically
4. User is redirected to dashboard

### Protected Routes
- Auth state is checked in `AuthContext`
- `useAuth()` hook provides user info to components
- Redirect to login if not authenticated

## Files Created

- `supabaseClient.js` - Supabase client initialization
- `AuthContext.jsx` - Auth state management
- `Auth.jsx` - Updated with Supabase integration
- `main.jsx` - Updated with AuthProvider wrapper
- `.env.local` - Environment variables (add your credentials)

## Testing

1. Click "Start Exploring" on landing page
2. Click "Sign Up"
3. Enter email, password, and username
4. Check your email for confirmation link
5. After confirming, sign in with your credentials
6. You should be redirected to dashboard

## Troubleshooting

**"Invalid API key"** - Check your VITE_SUPABASE_ANON_KEY in .env.local

**"Email not confirmed"** - Check your email for confirmation link from Supabase

**"User already exists"** - Try signing in instead of signing up

**CORS errors** - Make sure your Supabase project allows your frontend URL
