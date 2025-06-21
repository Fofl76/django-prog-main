<template>
  <div>
    <AppHeader />

    <!-- Основной контент каталога -->
    <v-main class="catalog-main">
      <v-container>
        <!-- Заголовок и фильтры -->
        <v-row class="my-6">
          <v-col cols="12">
            <h1 class="text-h3 font-weight-bold primary--text">Каталог номеров</h1>
          </v-col>
        </v-row>

        <!-- Фильтры -->
        <v-row class="mb-6">
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.priceMin"
              label="Цена от"
              type="number"
              outlined
              dense
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-text-field
              v-model="filters.priceMax"
              label="Цена до"
              type="number"
              outlined
              dense
            ></v-text-field>
          </v-col>
          <v-col cols="12" md="3">
            <v-select
              v-model="filters.capacity"
              :items="capacityOptions"
              label="Вместимость"
              :item-title="'text'"
              :item-value="'value'"
              outlined
              dense
            ></v-select>
          </v-col>
          <v-col cols="12" md="3">
            <v-btn
              color="primary"
              block
              @click="applyFilters"
            >
              Применить фильтры
            </v-btn>
          </v-col>
        </v-row>

        <!-- Список номеров -->
        <v-row>
          <!-- Индикатор загрузки -->
          <v-col v-if="loading" cols="12" class="text-center">
            <v-progress-circular
              indeterminate
              color="primary"
              size="64"
            ></v-progress-circular>
          </v-col>

          <!-- Сообщение об ошибке -->
          <v-col v-else-if="error" cols="12">
            <v-alert
              type="error"
              text
            >
              {{ error }}
            </v-alert>
          </v-col>

          <!-- Сообщение, если нет номеров -->
          <v-col v-else-if="rooms.length === 0" cols="12" class="text-center">
            <v-alert
              type="info"
              text
            >
              По вашему запросу ничего не найдено
            </v-alert>
          </v-col>

          <!-- Список номеров -->
          <v-col
            v-else
            v-for="room in rooms"
            :key="room.id"
            cols="12"
            md="6"
            lg="4"
          >
            <v-card class="mx-auto" elevation="2">
              <v-img
                :src="getRoomPhoto(room)"
                height="250"
                cover
              ></v-img>
              <v-card-title>{{ room.room_type }}</v-card-title>
              <v-card-text>
                <div class="mb-2">Номер комнаты: {{ room.room_number }}</div>
                <div class="d-flex align-center mb-2">
                  <v-icon class="mr-1">mdi-account-group</v-icon>
                  <span>до {{ room.max_occupancy }} гостей</span>
                </div>
                <div class="d-flex flex-wrap">
                  <v-chip
                    v-for="amenity in room.amenities"
                    :key="amenity.id"
                    class="mr-1 mb-1"
                    small
                  >
                    {{ amenity.name }}
                  </v-chip>
                </div>
                <div class="text-h6 primary--text mt-2">
                  {{ room.price_per_night }} ₽/ночь
                </div>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  color="primary"
                  variant="text"
                  :to="'/rooms/' + room.id"
                >
                  Подробнее
                </v-btn>
                <v-spacer></v-spacer>
                <v-btn
                  color="primary"
                  @click="bookRoom(room.id)"
                  :disabled="!room.is_available"
                >
                  {{ room.is_available ? 'Забронировать' : 'Недоступно' }}
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>

        <!-- Пагинация -->
        <v-row class="mt-6">
          <v-col cols="12" class="text-center">
            <v-pagination
              v-model="page"
              :length="totalPages"
              @update:modelValue="loadRooms"
            ></v-pagination>
          </v-col>
        </v-row>
      </v-container>
    </v-main>

    <AppFooter />
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { roomsAPI } from '@/services/api'
import AppHeader from './AppHeader.vue'
import AppFooter from './AppFooter.vue'

export default {
  name: 'RoomsCatalog',
  components: {
    AppHeader,
    AppFooter
  },
  data() {
    return {
      globalSearch: '',
      page: 1,
      totalPages: 1,
      filters: {
        priceMin: '',
        priceMax: '',
        capacity: null
      },
      capacityOptions: [
        { text: 'Все', value: null },
        { text: '1-2 человека', value: 2 },
        { text: '3-4 человека', value: 4 },
        { text: '5 и более', value: 5 }
      ],
      rooms: [],
      loading: false,
      error: null
    }
  },
  computed: {
    ...mapState(['isAuthenticated']),
    queryParams() {
      return {
        page: this.page,
        min_price: this.filters.priceMin || undefined,
        max_price: this.filters.priceMax || undefined,
        min_occupancy: this.filters.capacity || undefined,
        search: this.globalSearch || undefined
      }
    }
  },
  methods: {
    ...mapActions(['logout']),
    async loadRooms() {
      try {
        this.loading = true;
        this.error = null;
        const response = await roomsAPI.getRooms(this.queryParams);
        this.rooms = response.results;
        this.totalPages = Math.ceil(response.count / 10); // Предполагаем, что на странице 10 элементов
      } catch (error) {
        this.error = 'Ошибка при загрузке списка номеров';
        console.error('Ошибка при загрузке номеров:', error);
      } finally {
        this.loading = false;
      }
    },
    async handleGlobalSearch() {
      this.page = 1; // Сбрасываем страницу при новом поиске
      await this.loadRooms();
    },
    async handleLogout() {
      try {
        await this.logout();
        this.$router.push('/login');
      } catch (error) {
        console.error('Ошибка при выходе:', error);
      }
    },
    async applyFilters() {
      this.page = 1; // Сбрасываем страницу при применении фильтров
      await this.loadRooms();
    },
    async bookRoom(roomId) {
      if (!this.isAuthenticated) {
        this.$router.push('/login');
        return;
      }
      
      try {
        // Здесь будет логика создания бронирования
        const bookingData = {
          room: roomId,
          // Добавьте остальные необходимые данные
        };
        await roomsAPI.createBooking(bookingData);
        // Показать уведомление об успешном бронировании
      } catch (error) {
        console.error('Ошибка при бронировании:', error);
        // Показать уведомление об ошибке
      }
    },
    getRoomPhoto(room) {
      if (room.photo) return room.photo;
      return '/no-image.png';
    }
  },
  created() {
    this.loadRooms();
  }
}
</script>

<style scoped>
.catalog-main {
  margin-top: 70px; /* Отступ от фиксированного хедера */
}

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