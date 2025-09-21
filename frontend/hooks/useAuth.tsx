'use client'

import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { api, User } from '@/lib/api'
import Cookies from 'js-cookie'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }): JSX.Element {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const initAuth = async () => {
      const token = Cookies.get('access_token')
      if (token) {
        try {
          const userData = await api.getCurrentUser()
          setUser(userData)
        } catch (error) {
          console.error('Auth initialization error:', error)
          Cookies.remove('access_token')
        }
      }
      setIsLoading(false)
    }

    initAuth()
  }, [])

  const login = async (email: string, password: string) => {
    const { user: userData } = await api.login(email, password)
    setUser(userData)
  }

  const register = async (email: string, password: string, fullName: string) => {
    await api.register(email, password, fullName)
  }

  const logout = async () => {
    await api.logout()
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}