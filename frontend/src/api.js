import { supabase } from './supabaseClient'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function getAuthHeaders() {
  const { data: { session } } = await supabase.auth.getSession()
  return {
    'Authorization': `Bearer ${session?.access_token}`,
    'Content-Type': 'application/json',
  }
}

export async function apiCall(endpoint, options = {}) {
  const headers = await getAuthHeaders()
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      ...headers,
      ...options.headers,
    },
  })

  if (!response.ok) {
    const error = await response.json()
    throw new Error(error.detail || 'API error')
  }

  return response.json()
}

export const api = {
  getCurrentUser: () => apiCall('/users/me'),
  getTaste: () => apiCall('/users/me/taste'),
  updateTaste: (taste) => apiCall('/users/me/taste', {
    method: 'POST',
    body: JSON.stringify(taste),
  }),
  getRecommendations: () => apiCall('/users/me/recommendations'),
  rateAnime: (animeId, rating) => apiCall('/users/me/watch-history', {
    method: 'POST',
    body: JSON.stringify({ anime_id: animeId, rating }),
  }),
  getWatchHistory: () => apiCall('/users/me/watch-history'),
}
