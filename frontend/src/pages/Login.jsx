import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { getErrorMessages, loginUser } from '../api.js'
import Alert from '../components/Alert.jsx'
import Button from '../components/Button.jsx'
import Input from '../components/Input.jsx'
import Logo from '../components/Logo.jsx'
import { useAuth } from '../context/AuthContext.js'

function validateLogin(email, password) {
  const errors = {}

  if (!email.trim()) {
    errors.email = 'Email is required.'
  }

  if (!password) {
    errors.password = 'Password is required.'
  }

  return errors
}

function Login() {
  const { login } = useAuth()
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  function handleEmailChange(event) {
    setEmail(event.target.value)
    setFieldErrors((current) => ({ ...current, email: '' }))
  }

  function handlePasswordChange(event) {
    setPassword(event.target.value)
    setFieldErrors((current) => ({ ...current, password: '' }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    setError('')

    const errors = validateLogin(email, password)
    setFieldErrors(errors)

    if (Object.keys(errors).length > 0) {
      return
    }

    setIsSubmitting(true)

    try {
      const data = await loginUser({ email: email.trim(), password })
      login(data.access_token)

      // replace: pressing Back afterwards won't return to the login form.
      navigate('/dashboard', { replace: true })
    } catch (requestError) {
      const { message, fieldErrors: apiFieldErrors } = getErrorMessages(requestError)

      setError(message)
      // The backend's login form calls the email field "username".
      setFieldErrors({
        email: apiFieldErrors.username,
        password: apiFieldErrors.password,
      })
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <section className="auth-page">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <div className="auth-header">
          <Logo />
          <h1>Welcome Back</h1>
          <p>Log in to view and manage your stock watchlist.</p>
        </div>

        <Input
          label="Email"
          name="email"
          type="email"
          value={email}
          onChange={handleEmailChange}
          placeholder="you@gmail.com"
          autoComplete="email"
          error={fieldErrors.email}
          required
        />
        <Input
          label="Password"
          name="password"
          type="password"
          value={password}
          onChange={handlePasswordChange}
          autoComplete="current-password"
          error={fieldErrors.password}
          required
        />

        {error && <Alert>{error}</Alert>}

        <Button type="submit" className="btn-block" disabled={isSubmitting}>
          {isSubmitting ? 'Logging in...' : 'Login'}
        </Button>

        <p className="auth-link">
          Don&apos;t have an account? <Link to="/signup">Sign up</Link>
        </p>
      </form>
    </section>
  )
}

export default Login
