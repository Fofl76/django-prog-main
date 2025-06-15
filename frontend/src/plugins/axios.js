import axios from 'axios'
import { useAuthStore } from '@/stores/auth'

// Базовый URL для всех запросов
axios.defaults.baseURL = 'http://localhost:8000'

// Перехватчик для обработки ответов
axios.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const authStore = useAuthStore()
      
      // Если токен просрочен, пробуем обновить его
      if (authStore.refreshToken) {
        try {
          await authStore.refreshToken()
          // Повторяем исходный запрос с новым токеном
          const config = error.config
          config.headers['Authorization'] = `Bearer ${authStore.accessToken}`
          return axios(config)
        } catch (refreshError) {
          // Если не удалось обновить токен, выходим из системы
          authStore.logout()
          return Promise.reject(refreshError)
        }
      }
    }
    return Promise.reject(error)
  }
)

// Перехватчик для добавления токена к запросам
axios.interceptors.request.use(
  (config) => {
    const authStore = useAuthStore()
    if (authStore.accessToken) {
      config.headers['Authorization'] = `Bearer ${authStore.accessToken}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
) 