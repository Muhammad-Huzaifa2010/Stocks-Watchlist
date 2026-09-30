import { Navigate, Outlet } from 'react-router-dom'
import { useAuth } from '../context/AuthContext.js'

// Wrap routes that need a logged-in user. Everyone else is sent to /login.
function ProtectedRoute() {
  const { isAuthenticated } = useAuth()

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <Outlet />
}

export default ProtectedRoute
