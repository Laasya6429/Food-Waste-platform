import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import './Layout.css'

const Layout = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="nav-brand">
          <h2>🌱 Food Waste Platform</h2>
        </div>
        <div className="nav-links">
          <Link to="/dashboard">Dashboard</Link>
          <Link to="/donations">Donations</Link>
          <Link to="/requests">Requests</Link>
          <Link to="/stats">Impact Stats</Link>
          <Link to="/heatmap">Heatmap</Link>
        </div>
        <div className="nav-user">
          <span>{user?.username} ({user?.role})</span>
          <button onClick={handleLogout}>Logout</button>
        </div>
      </nav>
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  )
}

export default Layout

