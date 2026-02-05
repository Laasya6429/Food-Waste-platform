import { createContext, useContext, useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const AuthContext = createContext(null)

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`
      // Fetch user profile
      fetchUserProfile()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUserProfile = async () => {
    try {
      // You'll need to create a user profile endpoint
      // For now, we'll decode the token to get user info
      const tokenData = JSON.parse(atob(token.split('.')[1]))
      setUser({
        id: tokenData.user_id,
        username: tokenData.username,
        role: tokenData.role,
      })
    } catch (error) {
      console.error('Error fetching user profile:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    try {
      const response = await api.post('/api/token/', { username, password })
      const { access, refresh } = response.data
      localStorage.setItem('token', access)
      localStorage.setItem('refresh', refresh)
      setToken(access)
      api.defaults.headers.common['Authorization'] = `Bearer ${access}`
      
      // Decode token to get user info
      const tokenData = JSON.parse(atob(access.split('.')[1]))
      setUser({
        id: tokenData.user_id,
        username: tokenData.username,
        role: tokenData.role,
      })
      
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Login failed',
      }
    }
  }

  const register = async (userData) => {
    try {
      await api.post('/api/register/', userData)
      return { success: true }
    } catch (error) {
      return {
        success: false,
        error: error.response?.data || 'Registration failed',
      }
    }
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('refresh')
    setToken(null)
    setUser(null)
    delete api.defaults.headers.common['Authorization']
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

