import { create } from 'zustand'
import { api } from '@/lib/api'

interface User {
  user_id: string
  email: string
  username: string
  is_active: boolean
  is_verified: boolean
  created_at: string
  last_login: string | null
  total_analyses: number
  total_uploads: number
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  login: (username: string, password: string) => Promise<void>
  register: (email: string, username: string, password: string) => Promise<void>
  logout: () => void
  fetchUser: () => Promise<void>
  updateUser: (user: User) => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,

  login: async (username: string, password: string) => {
    await api.login(username, password)
    const user = await api.getCurrentUser()
    set({ user, isAuthenticated: true })
  },

  register: async (email: string, username: string, password: string) => {
    await api.register(email, username, password)
    // Auto login after registration
    await api.login(username, password)
    const user = await api.getCurrentUser()
    set({ user, isAuthenticated: true })
  },

  logout: () => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    }
    set({ user: null, isAuthenticated: false })
  },

  fetchUser: async () => {
    try {
      set({ isLoading: true })
      const user = await api.getCurrentUser()
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  updateUser: (user: User) => {
    set({ user })
  },
}))
