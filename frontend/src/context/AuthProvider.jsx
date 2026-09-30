import { useCallback, useEffect, useState } from 'react'
import { AuthContext } from './AuthContext.js'

const TOKEN_KEY = 'stocks-watchlist.token'

// setTimeout cannot wait longer than about 24.8 days.
const MAX_TIMEOUT_MS = 2_147_483_647

// Reads "exp" from the JWT payload so the app knows when the session ends.
// This does not verify the token; the backend still checks it on every request.
function getTokenExpiry(token) {
  try {
    const payload = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    const { exp } = JSON.parse(atob(payload))

    return typeof exp === 'number' ? exp * 1000 : null
  } catch {
    return null
  }
}

function isTokenUsable(token) {
  const expiry = getTokenExpiry(token)

  return expiry !== null && expiry > Date.now()
}

// localStorage can throw when the browser blocks site storage.
// In that case the session still works, it just won't survive a reload.
function loadToken() {
  try {
    const token = localStorage.getItem(TOKEN_KEY)

    if (token && isTokenUsable(token)) {
      return token
    }

    localStorage.removeItem(TOKEN_KEY)
  } catch {
    // Storage unavailable: start logged out.
  }

  return null
}

function saveToken(token) {
  try {
    localStorage.setItem(TOKEN_KEY, token)
  } catch {
    // Storage unavailable: keep the session in memory only.
  }
}

function clearToken() {
  try {
    localStorage.removeItem(TOKEN_KEY)
  } catch {
    // Storage unavailable: nothing to clear.
  }
}

function AuthProvider({ children }) {
  const [token, setToken] = useState(loadToken)

  const login = useCallback((accessToken) => {
    if (!isTokenUsable(accessToken)) {
      throw new Error('The server returned an unusable access token.')
    }

    saveToken(accessToken)
    setToken(accessToken)
  }, [])

  const logout = useCallback(() => {
    clearToken()
    setToken(null)
  }, [])

  // Log out automatically when the token expires.
  useEffect(() => {
    if (!token) {
      return undefined
    }

    const msUntilExpiry = getTokenExpiry(token) - Date.now()
    const timer = setTimeout(logout, Math.min(msUntilExpiry, MAX_TIMEOUT_MS))

    return () => clearTimeout(timer)
  }, [token, logout])

  const value = {
    token,
    isAuthenticated: token !== null,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export default AuthProvider
