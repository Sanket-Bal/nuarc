import { useState } from 'react'
import './Home.css'

function Home({ onLogout }) {
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('all')

  const recommendations = [
    { id: 1, title: 'Demon Slayer', category: 'anime', rating: 9.1, image: '🎬' },
    { id: 2, title: 'Inception', category: 'movie', rating: 8.8, image: '🎭' },
    { id: 3, title: 'Attack on Titan', category: 'anime', rating: 9.0, image: '⚔️' },
    { id: 4, title: 'The Matrix', category: 'movie', rating: 8.7, image: '💻' },
    { id: 5, title: 'Jujutsu Kaisen', category: 'anime', rating: 8.9, image: '✨' },
    { id: 6, title: 'Interstellar', category: 'movie', rating: 8.6, image: '🚀' },
    { id: 7, title: 'Death Note', category: 'anime', rating: 8.8, image: '📓' },
    { id: 8, title: 'The Dark Knight', category: 'movie', rating: 9.0, image: '🦇' },
  ]

  const filteredRecommendations = recommendations.filter(item => {
    const matchesCategory = selectedCategory === 'all' || item.category === selectedCategory
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesCategory && matchesSearch
  })

  return (
    <div className="home-container">
      {/* Navigation */}
      <nav className="home-navbar">
        <div className="home-nav-container">
          <div className="home-logo">
            <span className="home-logo-text">Nuarc</span>
          </div>
          <button className="home-logout-button" onClick={onLogout}>
            Logout
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="home-hero">
        <div className="home-hero-content">
          <h1 className="home-hero-title">Welcome Back!</h1>
          <p className="home-hero-subtitle">Discover personalized recommendations just for you</p>
        </div>
      </section>

      {/* Search and Filter Section */}
      <section className="home-search-section">
        <div className="home-search-container">
          <div className="home-search-box">
            <input
              type="text"
              placeholder="Search movies and anime..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="home-search-input"
            />
            <span className="home-search-icon">🔍</span>
          </div>

          <div className="home-filters">
            <button
              className={`home-filter-button ${selectedCategory === 'all' ? 'active' : ''}`}
              onClick={() => setSelectedCategory('all')}
            >
              All
            </button>
            <button
              className={`home-filter-button ${selectedCategory === 'movie' ? 'active' : ''}`}
              onClick={() => setSelectedCategory('movie')}
            >
              Movies
            </button>
            <button
              className={`home-filter-button ${selectedCategory === 'anime' ? 'active' : ''}`}
              onClick={() => setSelectedCategory('anime')}
            >
              Anime
            </button>
          </div>
        </div>
      </section>

      {/* Recommendations Grid */}
      <section className="home-recommendations">
        <div className="home-recommendations-container">
          <h2 className="home-section-title">Recommended For You</h2>
          <div className="home-grid">
            {filteredRecommendations.map((item, index) => (
              <div
                key={item.id}
                className="home-card"
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="home-card-image">{item.image}</div>
                <div className="home-card-content">
                  <h3 className="home-card-title">{item.title}</h3>
                  <div className="home-card-meta">
                    <span className="home-card-category">{item.category}</span>
                    <span className="home-card-rating">⭐ {item.rating}</span>
                  </div>
                  <button className="home-card-button">View Details</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Background Orbs */}
      <div className="home-background">
        <div className="home-orb home-orb-1"></div>
        <div className="home-orb home-orb-2"></div>
        <div className="home-orb home-orb-3"></div>
      </div>
    </div>
  )
}

export default Home
