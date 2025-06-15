import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

export const roomsAPI = {
  // Получение списка комнат с фильтрацией
  getRooms: async (params) => {
    try {
      const response = await axios.get(`${API_URL}/rooms/`, { params });
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении списка комнат:', error);
      throw error;
    }
  },

  // Получение деталей конкретной комнаты
  getRoomDetails: async (roomId) => {
    try {
      const response = await axios.get(`${API_URL}/rooms/${roomId}/`);
      return response.data;
    } catch (error) {
      console.error('Ошибка при получении информации о комнате:', error);
      throw error;
    }
  },

  // Создание бронирования
  createBooking: async (bookingData) => {
    try {
      const response = await axios.post(`${API_URL}/bookings/`, bookingData);
      return response.data;
    } catch (error) {
      console.error('Ошибка при создании бронирования:', error);
      throw error;
    }
  }
}; 