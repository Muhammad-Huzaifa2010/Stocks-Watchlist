// Fallback to an empty string if VITE_API_URL is not defined, 
// allowing relative path routing (e.g., through an Nginx reverse proxy) in production.
const API_URL = import.meta.env.VITE_API_URL ?? ''


const GENERIC_ERROR = 'Something went wrong. Please try again later.'

// status 0 means no response arrived: the server is down, or the network/CORS blocked the request.
export class ApiError extends Error {
  constructor(status, detail = null) {
    super(`API request failed with status ${status}`)
    this.name = 'ApiError'
    this.status = status
    this.detail = detail
  }
}

async function request(path, options) {
  let response

  try {
    response = await fetch(`${API_URL}${path}`, options)
  } catch {
    throw new ApiError(0)
  }

  const data = await response.json().catch(() => null)

  if (!response.ok) {
    throw new ApiError(response.status, data?.detail ?? null)
  }

  return data
}

export function createUser({ username, email, password }) {
  return request('/users', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, email, password }),
  })
}

// FastAPI's OAuth2PasswordRequestForm expects form fields, and calls the email "username".
export function loginUser({ email, password }) {
  const body = new URLSearchParams({
    username: email,
    password,
  })

  return request('/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body,
  })
}

// The token proves to FastAPI who is asking.
function authHeaders(token) {
  return { Authorization: `Bearer ${token}` }
}

// GET is fetch's default method.
export function getStocks(token) {
  return request('/stocks', {
    headers: authHeaders(token),
  })
}

export function createStock(token, stockData) {
  return request('/stocks', {
    method: 'POST',
    headers: {
      ...authHeaders(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(stockData),
  })
}

// PUT replaces every field, so stockData must contain all five fields.
export function updateStock(token, stockId, stockData) {
  return request(`/stocks/${stockId}`, {
    method: 'PUT',
    headers: {
      ...authHeaders(token),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(stockData),
  })
}

export function deleteStock(token, stockId) {
  return request(`/stocks/${stockId}`, {
    method: 'DELETE',
    headers: authHeaders(token),
  })
}

// True when the backend rejected the token (missing, invalid or expired).
export function isUnauthorized(error) {
  return error instanceof ApiError && error.status === 401
}

// Converts an error from request() into messages that are safe to show to users.
export function getErrorMessages(error) {
  if (!(error instanceof ApiError)) {
    return { message: GENERIC_ERROR, fieldErrors: {} }
  }

  if (error.status === 0) {
    return {
      message: 'Unable to connect to the server. Please try again.',
      fieldErrors: {},
    }
  }

  // FastAPI validation errors: { detail: [{ loc: ['body', 'email'], msg: '...' }] }
  if (error.status === 422 && Array.isArray(error.detail)) {
    const fieldErrors = {}

    for (const item of error.detail) {
      const field = item.loc?.[0] === 'body' ? item.loc[1] : null

      if (field && typeof item.msg === 'string' && !fieldErrors[field]) {
        fieldErrors[field] = item.msg.replace(/^Value error, /, '')
      }
    }

    const hasFieldErrors = Object.keys(fieldErrors).length > 0

    return {
      message: hasFieldErrors ? '' : 'Please check your details and try again.',
      fieldErrors,
    }
  }

  if (error.status < 500 && typeof error.detail === 'string') {
    return { message: error.detail, fieldErrors: {} }
  }

  return { message: GENERIC_ERROR, fieldErrors: {} }
}