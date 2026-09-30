import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.js'
import Logo from './Logo.jsx'

const guestLinks = [
  { to: '/login', label: 'Login' },
  { to: '/signup', label: 'Signup' },
  { to: '/dashboard', label: 'Dashboard' },
]

const userLinks = [{ to: '/dashboard', label: 'Dashboard' }]

function Navbar() {
  const { isAuthenticated, logout } = useAuth()
  const navigate = useNavigate()
  const navLinks = isAuthenticated ? userLinks : guestLinks

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link className="navbar-brand" to="/dashboard">
          <Logo />
        </Link>

        <nav className="navbar-links" aria-label="Main navigation">
          {navLinks.map((link) => (
            <NavLink key={link.to} className="navbar-link" to={link.to}>
              {link.label}
            </NavLink>
          ))}

          {isAuthenticated && (
            <button className="navbar-link" type="button" onClick={handleLogout}>
              Logout
            </button>
          )}
        </nav>
      </div>
    </header>
  )
}

export default Navbar
