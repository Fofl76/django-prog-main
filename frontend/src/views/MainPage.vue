<template>
  <div>
    <!-- Верхняя панель (хедер) -->
    <v-app-bar 
      flat 
      color="white" 
      class="px-4"
      height="80"
    >
      <!-- Логотип слева -->
      <router-link 
        to="/" 
        class="text-decoration-none d-flex align-center"
      >
        <v-img
          src="@/assets/img/logo.png"
          max-width="180"
          contain
          class="mr-4"
        ></v-img>
      </router-link>

      <v-spacer></v-spacer>
      
      <!-- Поиск по центру -->
      <v-text-field
        v-model="globalSearch"
        prepend-inner-icon="mdi-magnify"
        placeholder="Поиск по сайту"
        single-line
        hide-details
        class="mx-4 search-field"
        style="max-width: 400px;"
        rounded
        filled
        dense
        @keyup.enter="handleGlobalSearch"
      ></v-text-field>

      <v-spacer></v-spacer>

      <!-- Кнопка каталога справа -->
      <v-btn
        color="primary"
        class="text-body-1 font-weight-medium mr-4"
        rounded
        to="/rooms"
      >
        Каталог
      </v-btn>

      <!-- Иконка личного кабинета -->
      <v-menu
        offset-y
        transition="slide-y-transition"
      >
        <template v-slot:activator="{ props }">
          <v-btn
            icon
            v-bind="props"
            class="ml-2"
          >
            <v-icon size="32">mdi-account-circle</v-icon>
          </v-btn>
        </template>

        <v-list>
          <template v-if="isAuthenticated">
            <v-list-item to="/profile">
              <v-list-item-title>Личный кабинет</v-list-item-title>
            </v-list-item>
            <v-list-item to="/bookings">
              <v-list-item-title>Мои бронирования</v-list-item-title>
            </v-list-item>
            <v-divider></v-divider>
            <v-list-item @click="handleLogout">
              <v-list-item-title>Выйти</v-list-item-title>
            </v-list-item>
          </template>
          <template v-else>
            <v-list-item to="/login">
              <v-list-item-title>Войти</v-list-item-title>
            </v-list-item>
            <v-list-item to="/register">
              <v-list-item-title>Зарегистрироваться</v-list-item-title>
            </v-list-item>
          </template>
        </v-list>
      </v-menu>
    </v-app-bar>

    <!-- Основной контент -->
    <v-main>
      <v-container fluid class="pa-0">
        <!-- Заголовок -->
        <v-row justify="center" class="my-8">
          <v-col cols="12" class="text-center">
            <h1 class="text-h3 font-weight-bold primary--text">
              С нами вы точно отдохнёте!
            </h1>
          </v-col>
        </v-row>

        <!-- Форма поиска -->
        <v-row justify="center" class="mb-8">
          <v-col cols="12" sm="10" md="8" lg="6">
            <v-card class="d-flex align-center" flat>
              <v-col>
                <v-text-field
                  v-model="checkIn"
                  label="Дата заезда"
                  type="date"
                  hide-details
                ></v-text-field>
              </v-col>
              <v-col>
                <v-text-field
                  v-model="checkOut"
                  label="Дата выезда"
                  type="date"
                  hide-details
                ></v-text-field>
              </v-col>
              <v-col>
                <v-select
                  v-model="guests"
                  :items="guestOptions"
                  label="Количество гостей"
                  hide-details
                ></v-select>
              </v-col>
              <v-col cols="auto">
                <v-btn
                  color="primary"
                  x-large
                  class="px-8"
                >
                  Подобрать
                </v-btn>
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
                v-for="(image, i) in roomImages"
                :key="i"
                :src="image"
                cover
              >
                <v-sheet
                  height="100%"
                  tile
                >
                  <v-row
                    class="fill-height"
                    align="center"
                    justify="center"
                  >
                  </v-row>
                </v-sheet>
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
              v-for="(tour, i) in tours"
              :key="i"
              cols="12"
              sm="6"
              md="4"
            >
              <v-card
                class="mx-auto"
                max-width="400"
              >
                <v-img
                  :src="tour.image"
                  height="200"
                  cover
                ></v-img>
                <v-card-title>{{ tour.title }}</v-card-title>
                <v-card-text>{{ tour.description }}</v-card-text>
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

export default {
  name: 'MainPage',
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
      roomImages: [
        'https://via.placeholder.com/800x600?text=Room+1',
        'https://via.placeholder.com/800x600?text=Room+2',
        'https://via.placeholder.com/800x600?text=Room+3',
        'https://via.placeholder.com/800x600?text=Room+4'
      ],
      tours: [
        {
          title: 'Джип-тур',
          image: 'https://via.placeholder.com/400x300?text=Tour+1',
          description: 'Захватывающее путешествие по горным маршрутам'
        },
        {
          title: 'Водные развлечения',
          image: 'https://via.placeholder.com/400x300?text=Tour+2',
          description: 'Активный отдых на воде'
        },
        {
          title: 'Морская прогулка',
          image: 'https://via.placeholder.com/400x300?text=Tour+3',
          description: 'Прогулка на катере вдоль побережья'
        },
        {
          title: 'Горные прогулки',
          image: 'https://via.placeholder.com/400x300?text=Tour+4',
          description: 'Пешие прогулки по живописным местам'
        },
        {
          title: 'Экскурсии',
          image: 'https://via.placeholder.com/400x300?text=Tour+5',
          description: 'Посещение исторических мест'
        },
        {
          title: 'Достопримечательности',
          image: 'https://via.placeholder.com/400x300?text=Tour+6',
          description: 'Знакомство с местной архитектурой'
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
    async handleLogout() {
      try {
        await this.logout()
        this.$router.push('/login')
      } catch (error) {
        console.error('Ошибка при выходе:', error)
      }
    }
  }
}
</script>

<style scoped>
.search-field {
  background-color: #f5f5f5;
  border-radius: 24px !important;
}

.search-field :deep(.v-field__input) {
  padding: 8px 16px;
}

.search-field :deep(.v-field__prepend-inner) {
  padding-left: 12px;
}

.v-btn {
  text-transform: none !important;
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
</style>