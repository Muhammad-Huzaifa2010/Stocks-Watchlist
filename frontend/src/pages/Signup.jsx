import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { createUser, getErrorMessages } from '../api.js'
import Alert from '../components/Alert.jsx'
import Button from '../components/Button.jsx'
import Input from '../components/Input.jsx'
import Logo from '../components/Logo.jsx'

const initialValues = {
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
}

function validateSignup(values) {
  const errors = {}

  if (!values.username.trim()) {
    errors.username = 'Username is required.'
  }

  if (!values.email.trim()) {
    errors.email = 'Email is required.'
  }

  if (!values.password) {
    errors.password = 'Password is required.'
  }

  if (!values.confirmPassword) {
    errors.confirmPassword = 'Please confirm your password.'
  } else if (values.password !== values.confirmPassword) {
    errors.confirmPassword = 'Passwords do not match.'
  }

  return errors
}

function Signup() {
  const [values, setValues] = useState(initialValues)
  const [fieldErrors, setFieldErrors] = useState({})
  const [formError, setFormError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSuccess, setIsSuccess] = useState(false)
  const successHeadingRef = useRef(null)

  // Move focus to the success heading so screen reader users hear the result.
  useEffect(() => {
    if (isSuccess) {
      successHeadingRef.current?.focus()
    }
  }, [isSuccess])

  function handleChange(event) {
    const { name, value } = event.target

    setValues((current) => ({ ...current, [name]: value }))
    setFieldErrors((current) => ({ ...current, [name]: '' }))
  }

  async function handleSubmit(event) {
    event.preventDefault()

    if (isSubmitting) {
      return
    }

    setFormError('')

    const errors = validateSignup(values)
    setFieldErrors(errors)

    if (Object.keys(errors).length > 0) {
      return
    }

    setIsSubmitting(true)

    try {
      await createUser({
        username: values.username.trim(),
        email: values.email.trim(),
        password: values.password,
      })

      setValues(initialValues)
      setIsSuccess(true)
    } catch (error) {
      const { message, fieldErrors: apiFieldErrors } = getErrorMessages(error)
      setFormError(message)
      setFieldErrors(apiFieldErrors)
    } finally {
      setIsSubmitting(false)
    }
  }

  if (isSuccess) {
    return (
      <section className="auth-page">
        <div className="card auth-card">
          <div className="auth-header">
            <Logo />
            <h1 ref={successHeadingRef} tabIndex={-1}>
              Account Created
            </h1>
          </div>

          <Alert variant="success">
            Account created successfully. You can now log in.
          </Alert>

          <Link className="btn btn-block" to="/login">
            Go to Login
          </Link>
        </div>
      </section>
    )
  }

  return (
    <section className="auth-page">
      <form className="card auth-card" onSubmit={handleSubmit}>
        <div className="auth-header">
          <Logo />
          <h1>Create Your Account</h1>
          <p>Start tracking the stocks you care about in one place.</p>
        </div>

        <Input
          label="Username"
          name="username"
          value={values.username}
          onChange={handleChange}
          autoComplete="username"
          error={fieldErrors.username}
          required
        />
        <Input
          label="Gmail address"
          name="email"
          type="email"
          value={values.email}
          onChange={handleChange}
          placeholder="you@gmail.com"
          autoComplete="email"
          error={fieldErrors.email}
          required
        />
        <Input
          label="Password"
          name="password"
          type="password"
          value={values.password}
          onChange={handleChange}
          autoComplete="new-password"
          error={fieldErrors.password}
          required
        />
        <Input
          label="Confirm password"
          name="confirmPassword"
          type="password"
          value={values.confirmPassword}
          onChange={handleChange}
          autoComplete="new-password"
          error={fieldErrors.confirmPassword}
          required
        />

        {formError && <Alert>{formError}</Alert>}

        <Button type="submit" className="btn-block" disabled={isSubmitting}>
          {isSubmitting ? 'Creating account...' : 'Signup'}
        </Button>

        <p className="auth-link">
          Already have an account? <Link to="/login">Log in</Link>
        </p>
      </form>
    </section>
  )
}

export default Signup
