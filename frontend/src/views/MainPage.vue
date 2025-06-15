<template>
  <div>
    <!-- Импортированный хедер -->
    <AppHeader />

    <!-- Основной контент -->
    <v-main>
      <v-container fluid class="pa-0">
        <!-- Заголовок -->
        <v-row justify="center" class="mt-20">
          <v-col cols="12" class="text-center">
            <h1 class="text-h3 font-weight-bold primary--text">
              С нами вы точно отдохнёте!
            </h1>
          </v-col>
        </v-row>

        <!-- Форма поиска -->
        <v-row justify="center" class="mb-8">
          <v-col cols="12" sm="10" md="8" lg="6">
            <v-card class="search-form" flat>
              <v-col>
                <input
                  v-model="checkIn"
                  type="date"
                  placeholder="Дата заезда"
                  class="search-input"
                />
              </v-col>
              <v-col>
                <input
                  v-model="checkOut"
                  type="date"
                  placeholder="Дата выезда"
                  class="search-input"
                />
              </v-col>
              <v-col>
                <select
                  v-model="guests"
                  class="search-input"
                >
                  <option v-for="option in guestOptions" :key="option" :value="option">
                    {{ option }}
                  </option>
                </select>
              </v-col>
              <v-col cols="auto">
                <button class="search-button">
                  Подобрать
                </button>
              </v-col>
            </v-card>
          </v-col>
        </v-row>

        <!-- Галерея изображений -->
        <v-row class="mb-8">
          <v-col cols="12">
            <v-carousel
              hide-delimiters
              show-arrows="hover"
              height="500"
            >
              <v-carousel-item
                v-for="(image, i) in sliderImages"
                :key="i"
                :src="image.image"
                cover
              >
                <template v-slot:placeholder>
                  <v-row
                    class="fill-height ma-0"
                    align="center"
                    justify="center"
                  >
                    <v-progress-circular
                      indeterminate
                      color="primary"
                    ></v-progress-circular>
                  </v-row>
                </template>
              </v-carousel-item>
            </v-carousel>
          </v-col>
        </v-row>

        <!-- Специальные предложения -->
        <v-container>
          <h2 class="text-h4 font-weight-bold text-center mb-6">
            Специальные предложения и туры
          </h2>
          <v-row>
            <v-col
              v-for="(offer, i) in specialOffers"
              :key="i"
              cols="12"
              sm="6"
              md="4"
            >
              <v-card
                class="mx-auto offer-card"
                max-width="400"
                @click="openOfferDetails(offer)"
              >
                <v-img
                  :src="offer.image"
                  height="200"
                  cover
                ></v-img>
                <v-card-title>{{ offer.title }}</v-card-title>
                <v-card-text>{{ offer.short_description }}</v-card-text>
                <v-card-actions v-if="offer.price">
                  <v-spacer></v-spacer>
                  <span class="text-h6 primary--text">{{ offer.price }} ₽</span>
                </v-card-actions>
              </v-card>
            </v-col>
          </v-row>
        </v-container>

        <!-- Модальное окно с деталями предложения -->
        <v-dialog
          v-model="showOfferDialog"
          max-width="800"
        >
          <v-card v-if="selectedOffer">
            <v-img
              :src="selectedOffer.image"
              height="300"
              cover
            ></v-img>
            <v-card-title class="text-h4">
              {{ selectedOffer.title }}
            </v-card-title>
            <v-card-text>
              <p class="text-body-1">{{ selectedOffer.full_description }}</p>
              <v-divider class="my-4"></v-divider>
              <div v-if="selectedOffer.price" class="text-h5 primary--text">
                Цена: {{ selectedOffer.price }} ₽
              </div>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                color="primary"
                @click="showOfferDialog = false"
              >
                Закрыть
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>

        <!-- Недавние отзывы -->
        <v-container class="mt-12">
          <h2 class="text-h4 font-weight-bold text-center mb-6">
            Недавние отзывы
          </h2>
          <v-row>
            <v-col
              v-for="(review, i) in recentReviews"
              :key="i"
              cols="12"
              sm="6"
              md="4"
            >
              <v-card class="mx-auto review-card" max-width="400">
                <v-card-text>
                  <div class="d-flex align-center mb-2">
                    <v-avatar color="primary" size="40" class="mr-3">
                      {{ review.author.charAt(0) }}
                    </v-avatar>
                    <div>
                      <div class="font-weight-bold">{{ review.author }}</div>
                      <div class="text-caption">{{ review.date }}</div>
                    </div>
                  </div>
                  <div class="mb-2">
                    <v-rating
                      v-model="review.rating"
                      readonly
                      dense
                      color="amber"
                      background-color="grey lighten-1"
                      half-increments
                    ></v-rating>
                  </div>
                  <p class="review-text">{{ review.text }}</p>
                </v-card-text>
              </v-card>
            </v-col>
          </v-row>
        </v-container>
      </v-container>
    </v-main>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import AppHeader from './Header.vue'
import axios from 'axios'

// Устанавливаем базовый URL для всех запросов
axios.defaults.baseURL = 'http://localhost:8000'

export default {
  name: 'MainPage',
  components: {
    AppHeader
  },
  data() {
    return {
      globalSearch: '',
      search: '',
      checkIn: '',
      checkOut: '',
      guests: '2 взрослых',
      guestOptions: [
        '1 взрослый',
        '2 взрослых',
        '3 взрослых',
        '4 взрослых'
      ],
      sliderImages: [],
      specialOffers: [],
      showOfferDialog: false,
      selectedOffer: null,
      recentReviews: [
        {
          author: 'Анна Петрова',
          date: '15.03.2024',
          rating: 5,
          text: 'Отличный отдых! Прекрасный сервис, уютные номера и внимательный персонал. Обязательно вернемся сюда снова.'
        },
        {
          author: 'Иван Смирнов',
          date: '10.03.2024',
          rating: 4.5,
          text: 'Хороший гостевой дом с отличным расположением. Особенно понравились экскурсии и местная кухня.'
        },
        {
          author: 'Мария Иванова',
          date: '05.03.2024',
          rating: 5,
          text: 'Прекрасное место для семейного отдыха. Дети в восторге от бассейна и развлекательной программы.'
        }
      ]
    }
  },
  computed: {
    ...mapState(['isAuthenticated']),
    defaultDates() {
      const today = new Date()
      const tomorrow = new Date(today)
      tomorrow.setDate(tomorrow.getDate() + 1)
      
      return {
        checkIn: today.toISOString().split('T')[0],
        checkOut: tomorrow.toISOString().split('T')[0]
      }
    }
  },
  methods: {
    ...mapActions(['logout']),
    handleGlobalSearch() {
      // Здесь будет логика глобального поиска
      console.log('Поиск:', this.globalSearch)
    },
    async fetchSliderImages() {
      try {
        console.log('Начинаем загрузку изображений слайдера...')
        const response = await axios.get('/api/slider-images/')
        console.log('Ответ от сервера:', response)
        console.log('Полученные изображения:', response.data)
        
        // Проверяем формат данных и добавляем полный URL для изображений
        this.sliderImages = response.data.map(image => {
          console.log('Обработка изображения:', image)
          // Убедимся, что URL изображения начинается с /media/
          // Удаляем эту логику, так как полный URL уже приходит с бэкенда
          return {
            ...image,
            image: image.image // Используем URL как есть
          }
        })
        
        console.log('sliderImages после обработки:', this.sliderImages)
      } catch (error) {
        console.error('Ошибка при загрузке изображений слайдера:', error)
        console.error('Детали ошибки:', error.response || error.message)
      }
    },
    async fetchSpecialOffers() {
      try {
        const response = await axios.get('/api/special-offers/')
        this.specialOffers = response.data
      } catch (error) {
        console.error('Ошибка при загрузке специальных предложений:', error)
      }
    },
    openOfferDetails(offer) {
      this.selectedOffer = offer
      this.showOfferDialog = true
    },
    async handleLogout() {
      try {
        await this.logout()
        this.$router.push('/login')
      } catch (error) {
        console.error('Ошибка при выходе:', error)
      }
    }
  },
  async created() {
    await this.fetchSliderImages()
    await this.fetchSpecialOffers()
  }
}
</script>

<style scoped>
.search-form {
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: #fff;
  padding: 10px;
  border-radius: 20px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.search-input {
  padding: 5px 10px;
  border: 2px solid #007bff;
  border-radius: 20px;
  width: 100%;
  outline: none;
}

.search-input:focus {
  border-color: #0056b3;
}

.search-button {
  padding: 5px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  white-space: nowrap;
}

.search-button:hover {
  background-color: #0056b3;
}

/* Стили для активной ссылки логотипа */
.router-link-active {
  opacity: 1;
}

/* Анимация при наведении на кнопки */
.v-btn:not(.v-btn--icon) {
  transition: transform 0.2s;
}

.v-btn:not(.v-btn--icon):hover {
  transform: translateY(-2px);
}

/* Медиа-запросы для адаптивности */
@media (max-width: 960px) {
  .search-field {
    max-width: 300px !important;
  }
}

@media (max-width: 600px) {
  .search-field {
    max-width: 200px !important;
  }
  
  .v-btn:not(.v-btn--icon) {
    font-size: 14px;
  }
}
.v-main{
  margin-top: 180px;
}

.review-card {
  transition: transform 0.2s;
}

.review-card:hover {
  transform: translateY(-5px);
}

.review-text {
  color: #666;
  line-height: 1.6;
  font-size: 0.95rem;
}

.offer-card {
  transition: transform 0.2s;
  cursor: pointer;
}

.offer-card:hover {
  transform: translateY(-5px);
}

.text-shadow {
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}
</style>