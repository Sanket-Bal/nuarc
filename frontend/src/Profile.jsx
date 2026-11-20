import { useState } from 'react'
import './Profile.css'

function Profile({ onBack }) {
  const [isEditing, setIsEditing] = useState(false)
  const [profileData, setProfileData] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    favoriteGenres: ['Action', 'Sci-Fi', 'Thriller'],
    joinDate: 'January 2024'
  })

  const [editData, setEditData] = useState(profileData)
  const [selectedGenres, setSelectedGenres] = useState(profileData.favoriteGenres)

  const allGenres = ['Action', 'Comedy', 'Drama', 'Horror', 'Romance', 'Sci-Fi', 'Thriller', 'Animation']

  const handleEditChange = (e) => {
    const { name, value } = e.target
    setEditData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleGenreToggle = (genre) => {
    setSelectedGenres(prev => {
      if (prev.includes(genre)) {
        return prev.filter(g => g !== genre)
      } else {
        return [...prev, genre]
      }
    })
  }

  const handleSaveChanges = () => {
    setProfileData({
      ...editData,
      favoriteGenres: selectedGenres
    })
    setIsEditing(false)
  }

  const handleCancel = () => {
    setEditData(profileData)
    setSelectedGenres(profileData.favoriteGenres)
    setIsEditing(false)
  }

  return (
    <div className="profile-container">
      {/* Navigation */}
      <nav className="profile-navbar">
        <div className="profile-nav-container">
          <button className="profile-back-button" onClick={onBack}>
            ←
          </button>
          <div className="profile-logo">
            <span className="profile-logo-text">Nuarc</span>
          </div>
          <div style={{ width: '100px' }}></div>
        </div>
      </nav>

      {/* Profile Header */}
      <section className="profile-header">
        <div className="profile-header-content">
          <div className="profile-avatar">👤</div>
          <h1 className="profile-name">{profileData.name}</h1>
          <p className="profile-email">{profileData.email}</p>
          <p className="profile-join-date">Member since {profileData.joinDate}</p>
        </div>
      </section>

      {/* Profile Content */}
      <section className="profile-content">
        <div className="profile-container-inner">
          {/* Stats Section */}
          <div className="profile-stats">
            <div className="profile-stat-card">
              <div className="profile-stat-icon">⭐</div>
              <div className="profile-stat-info">
                <p className="profile-stat-label">Favorite Genres</p>
                <div className="profile-genre-tags">
                  {profileData.favoriteGenres.map(genre => (
                    <span key={genre} className="profile-genre-tag">{genre}</span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Edit Profile Section */}
          <div className="profile-edit-section">
            <div className="profile-section-header">
              <h2 className="profile-section-title">Profile Information</h2>
              {!isEditing && (
                <button 
                  className="profile-edit-button"
                  onClick={() => setIsEditing(true)}
                >
                  ✏️ Edit Profile
                </button>
              )}
            </div>

            {isEditing ? (
              <form className="profile-form">
                <div className="profile-form-group">
                  <label htmlFor="name">Full Name</label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={editData.name}
                    onChange={handleEditChange}
                  />
                </div>

                <div className="profile-form-group">
                  <label htmlFor="email">Email Address</label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={editData.email}
                    onChange={handleEditChange}
                  />
                </div>

                <div className="profile-form-group">
                  <label>Favorite Genres</label>
                  <div className="profile-genre-selector">
                    {allGenres.map(genre => (
                      <button
                        key={genre}
                        type="button"
                        className={`profile-genre-button ${selectedGenres.includes(genre) ? 'active' : ''}`}
                        onClick={() => handleGenreToggle(genre)}
                      >
                        {genre}
                      </button>
                    ))}
                  </div>
                </div>

                <div className="profile-form-actions">
                  <button 
                    type="button"
                    className="profile-save-button"
                    onClick={handleSaveChanges}
                  >
                    Save Changes
                  </button>
                  <button 
                    type="button"
                    className="profile-cancel-button"
                    onClick={handleCancel}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            ) : (
              <div className="profile-info-display">
                <div className="profile-info-item">
                  <span className="profile-info-label">Full Name:</span>
                  <span className="profile-info-value">{profileData.name}</span>
                </div>
                <div className="profile-info-item">
                  <span className="profile-info-label">Email:</span>
                  <span className="profile-info-value">{profileData.email}</span>
                </div>
                <div className="profile-info-item">
                  <span className="profile-info-label">Favorite Genres:</span>
                  <div className="profile-genre-tags">
                    {profileData.favoriteGenres.map(genre => (
                      <span key={genre} className="profile-genre-tag">{genre}</span>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Preferences Section */}
          <div className="profile-preferences-section">
            <h2 className="profile-section-title">Preferences</h2>
            <div className="profile-preferences-grid">
              <div className="profile-preference-card">
                <h3>Notifications</h3>
                <p>Get notified about new recommendations</p>
                <label className="profile-toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="profile-toggle-slider"></span>
                </label>
              </div>
              <div className="profile-preference-card">
                <h3>Dark Mode</h3>
                <p>Always use dark theme</p>
                <label className="profile-toggle">
                  <input type="checkbox" defaultChecked />
                  <span className="profile-toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Background Orbs */}
      <div className="profile-background">
        <div className="profile-orb profile-orb-1"></div>
        <div className="profile-orb profile-orb-2"></div>
        <div className="profile-orb profile-orb-3"></div>
      </div>
    </div>
  )
}

export default Profile
