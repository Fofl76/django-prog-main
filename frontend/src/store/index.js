import { createStore } from 'vuex'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default createStore({
  state: {
    isAuthenticated: false,
    user: null,
    rooms: [],
    bookings: [],
    reviews: []
  },
  mutations: {
    setAuth(state, status) {
      state.isAuthenticated = status
    },
    setUser(state, user) {
      state.user = user
    },
    setRooms(state, rooms) {
      state.rooms = rooms
    },
    setBookings(state, bookings) {
      state.bookings = bookings
    },
    setReviews(state, reviews) {
      state.reviews = reviews
    }
  },
  actions: {
    async login({ commit }, credentials) {
      // TODO: Implement login logic
      commit('setAuth', true)
    },
    async logout({ commit }) {
      // TODO: Implement logout logic
      commit('setAuth', false)
      commit('setUser', null)
    },
    async fetchRooms({ commit }) {
      try {
        const response = await axios.get(`${API_URL}/rooms/`)
        commit('setRooms', response.data)
      } catch (error) {
        console.error('Error fetching rooms:', error)
      }
    },
    async bookRoom({ commit }, bookingData) {
      try {
        const response = await axios.post(`${API_URL}/bookings/`, bookingData)
        return response.data
      } catch (error) {
        throw error
      }
    },
    async fetchBookings({ commit }) {
      try {
        const response = await axios.get(`${API_URL}/bookings/`)
        commit('setBookings', response.data)
      } catch (error) {
        console.error('Error fetching bookings:', error)
      }
    }
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    user: state => state.user
  }
}) 