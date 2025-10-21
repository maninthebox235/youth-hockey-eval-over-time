import React, { createContext, useContext, useState, useEffect } from 'react'

interface User {
  id: number
  email: string
  username: string
  full_name: string | null
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      fetchCurrentUser(storedToken)
    } else {
      setIsLoading(false)
    }
  }, [])

  const fetchCurrentUser = async (authToken: string) => {
    try {
      const response = await fetch(`${API_URL}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${authToken}`
        }
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
      } else if (response.status === 401 || response.status === 403) {
        // Auth error - clear token
        localStorage.removeItem('token')
        setToken(null)
      } else {
        // Other HTTP error - keep token for retry
        console.error('Server error, keeping token for retry:', response.status)
      }
    } catch (error) {
      // Network error - keep token, user might be offline
      if (error instanceof TypeError && error.message.includes('fetch')) {
        console.error('Network error, keeping token:', error)
      } else {
        // Other errors - clear token
        console.error('Failed to fetch user:', error)
        localStorage.removeItem('token')
        setToken(null)
      }
    } finally {
      setIsLoading(false)
    }
  }

  const login = async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await fetch(`${API_URL}/api/auth/login`, {
      method: 'POST',
      body: formData
    })

    if (!response.ok) {
      try {
        const error = await response.json()
        throw new Error(error.detail || 'Login failed')
      } catch (parseError) {
        throw new Error(`Login failed: ${response.status} ${response.statusText}`)
      }
    }

    const data = await response.json()
    const authToken = data.access_token

    localStorage.setItem('token', authToken)
    setToken(authToken)

    await fetchCurrentUser(authToken)
  }

  const register = async (email: string, username: string, password: string, fullName?: string) => {
    const response = await fetch(`${API_URL}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email,
        username,
        password,
        full_name: fullName
      })
    })

    if (!response.ok) {
      try {
        const error = await response.json()
        throw new Error(error.detail || 'Registration failed')
      } catch (parseError) {
        throw new Error(`Registration failed: ${response.status} ${response.statusText}`)
      }
    }

    await login(username, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}
