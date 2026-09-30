import { Link } from 'react-router-dom'

function NotFound() {
  return (
    <main className="not-found">
      <p className="not-found-code">404</p>
      <h1>Page not found</h1>
      <p>The page you are looking for does not exist.</p>
      <Link className="btn" to="/login">
        Go to Login
      </Link>
    </main>
  )
}

export default NotFound
