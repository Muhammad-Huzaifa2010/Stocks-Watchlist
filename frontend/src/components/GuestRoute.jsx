import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.js'

// Wrap routes that only make sense when logged out (login, signup).
// Logged-in users are sent to /dashboard instead.
function GuestRoute() {
  const { isAuthenticated } = useAuth()

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return <Outlet />
}

export default GuestRoute
