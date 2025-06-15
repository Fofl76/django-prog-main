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

    <!-- Основной контент каталога -->
    <v-main>
      <v-container>
        <!-- Заголовок и фильтры -->
        <v-row class="my-6">
          <v-col cols="12" md="8">
            <h1 class="text-h3 font-weight-bold primary--text">Каталог номеров</h1>
          </v-col>
          <v-col cols="12" md="4">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="Сортировать по"
              hide-details
              outlined
              dense
            ></v-select>
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
                :src="room.image || 'https://via.placeholder.com/400x300?text=No+Image'"
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
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'
import { roomsAPI } from '@/services/api'

export default {
  name: 'RoomsCatalog',
  data() {
    return {
      globalSearch: '',
      page: 1,
      totalPages: 1,
      sortBy: 'price_asc',
      sortOptions: [
        { text: 'Цена (по возрастанию)', value: 'price_asc' },
        { text: 'Цена (по убыванию)', value: 'price_desc' },
        { text: 'Популярные', value: 'popular' }
      ],
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
        ordering: this.sortBy === 'price_asc' ? 'price_per_night' : 
                 this.sortBy === 'price_desc' ? '-price_per_night' : 
                 '-reviews__rating',
        price_min: this.filters.priceMin || undefined,
        price_max: this.filters.priceMax || undefined,
        max_occupancy: this.filters.capacity || undefined,
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
    }
  },
  watch: {
    queryParams: {
      handler() {
        this.loadRooms();
      },
      deep: true
    }
  },
  created() {
    this.loadRooms();
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