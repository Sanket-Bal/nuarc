import './App.css'
import { useEffect, useState } from 'react'

function App() {
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const handleScroll = () => {
      setScrollY(window.scrollY)
    }

    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  const toggleMenu = () => {
    const hamburger = document.getElementById('hamburger')
    const navLinks = document.getElementById('nav-links')
    hamburger.classList.toggle('active')
    navLinks.classList.toggle('active')
  }

  const closeMenu = () => {
    const hamburger = document.getElementById('hamburger')
    const navLinks = document.getElementById('nav-links')
    hamburger.classList.remove('active')
    navLinks.classList.remove('active')
  }

  useEffect(() => {
    const handleClickOutside = (event) => {
      const navbar = document.querySelector('.navbar')
      const hamburger = document.getElementById('hamburger')
      const navLinks = document.getElementById('nav-links')
      
      if (navbar && !navbar.contains(event.target)) {
        hamburger.classList.remove('active')
        navLinks.classList.remove('active')
      }
    }

    document.addEventListener('click', handleClickOutside)
    return () => document.removeEventListener('click', handleClickOutside)
  }, [])

  return (
    <div className="app">
      {/* Navigation */}
      <nav className="navbar">
        <div className="nav-container">
          <div className="logo">
            <span className="logo-text">Nuarc</span>
          </div>
          <button className="hamburger" id="hamburger" onClick={toggleMenu}>
            <span></span>
            <span></span>
            <span></span>
          </button>
          <ul className="nav-links" id="nav-links">
            <li><a href="#features" onClick={closeMenu}>Features</a></li>
            <li><a href="#how-it-works" onClick={closeMenu}>How It Works</a></li>
            <li><a href="#cta" onClick={closeMenu}>Get Started</a></li>
          </ul>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="hero">
        {/* Hero Image with Parallax */}
        <div className="hero-image" style={{ transform: `translateY(${scrollY * 0.5}px)` }}>
          <img src="/landing-page/horizontal.jpeg" alt="Hero" className="hero-img-desktop" />
          <img src="/landing-page/vertical.jpeg" alt="Hero" className="hero-img-mobile" />
        </div>

        {/* Animated Background Elements */}
        <div className="hero-background"></div>

        {/* Hero Content with Parallax */}
        <div className="hero-content" style={{ transform: `translateY(${scrollY * 0.2}px)` }}>
          <h1 className="hero-title" style={{fontSize: ``}}>
            Nuarc
          </h1>
          <p className="hero-subtitle">
            AI-powered recommendations for movies and anime tailored just for you
          </p>
          <button className="cta-button">Start Exploring</button>
        </div>

        {/* Gradient Orbs */}
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </section>

      {/* Features Section */}
      <section className="features" id="features">
        <h2 className="section-title">Why Choose Nuarc?</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered</h3>
            <p>Smart algorithms learn your taste and suggest exactly what you'll love</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🎯</div>
            <h3>Personalized</h3>
            <p>Get recommendations based on your unique preferences and viewing history</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">🌍</div>
            <h3>Vast Library</h3>
            <p>Access thousands of movies and anime from around the world</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Lightning Fast</h3>
            <p>Get instant recommendations without waiting</p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="how-it-works" id="how-it-works">
        <h2 className="section-title">How It Works</h2>
        <div className="steps-container">
          <div className="step">
            <div className="step-number">1</div>
            <h3>Rate Your Favorites</h3>
            <p>Tell us what you love</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">2</div>
            <h3>AI Analyzes</h3>
            <p>Our algorithm learns your taste</p>
          </div>
          <div className="step-arrow">→</div>
          <div className="step">
            <div className="step-number">3</div>
            <h3>Get Recommendations</h3>
            <p>Discover your next favorite</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section" id="cta">
        <div className="cta-content">
          <h2>Ready to Find Your Next Obsession?</h2>
          <p>Join thousands of movie and anime enthusiasts discovering their perfect match</p>
          <button className="cta-button-large">Get Started Now</button>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <p>&copy; 2024 Nuarc. All rights reserved.</p>
      </footer>
    </div>
  )
}

export default App
