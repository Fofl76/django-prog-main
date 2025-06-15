import { defineStore } from 'pinia'
import axios from 'axios'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: JSON.parse(localStorage.getItem('user')) || null
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    getUser: (state) => state.user
  },

  actions: {
    async login({ username, password }) {
      try {
        const response = await axios.post('/api/token/', {
          username,
          password
        })

        this.accessToken = response.data.access
        this.refreshToken = response.data.refresh
        
        localStorage.setItem('accessToken', this.accessToken)
        localStorage.setItem('refreshToken', this.refreshToken)
        
        // Настраиваем axios для использования токена
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
        
        return response
      } catch (error) {
        throw error
      }
    },

    async register({ username, email, password1, password2 }) {
      try {
        const response = await axios.post('/api/register/', {
          username,
          email,
          password: password1,
          password2: password2
        })
        return response
      } catch (error) {
        throw error
      }
    },

    async refreshToken() {
      try {
        const response = await axios.post('/api/token/refresh/', {
          refresh: this.refreshToken
        })
        
        this.accessToken = response.data.access
        localStorage.setItem('accessToken', this.accessToken)
        
        axios.defaults.headers.common['Authorization'] = `Bearer ${this.accessToken}`
        
        return response
      } catch (error) {
        this.logout()
        throw error
      }
    },

    logout() {
      this.accessToken = null
      this.refreshToken = null
      this.user = null
      
      localStorage.removeItem('accessToken')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
      
      delete axios.defaults.headers.common['Authorization']
    }
  }
}) 