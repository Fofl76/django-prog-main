<script>
import { useAuthStore } from '@/stores/auth'
import { storeToRefs } from 'pinia'
import { useRouter } from 'vue-router'

export default {
  name: 'App',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const { isAuthenticated } = storeToRefs(authStore)

    const handleLogout = async () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      isAuthenticated,
      handleLogout
    }
  }
}
</script>

<template>
  <v-app>
    <v-app-bar app color="primary">
      <v-app-bar-title>
        <router-link to="/" class="text-white text-decoration-none">
          Гостевой дом
        </router-link>
      </v-app-bar-title>

      <v-spacer></v-spacer>

      <v-btn to="/rooms" text class="text-white">
        Номера
      </v-btn>

      <template v-if="isAuthenticated">
        <v-btn to="/bookings" text class="text-white">
          Мои бронирования
        </v-btn>
        <v-btn to="/profile" text class="text-white">
          Профиль
        </v-btn>
        <v-btn @click="handleLogout" text class="text-white">
          Выйти
        </v-btn>
      </template>

      <template v-else>
        <v-btn to="/login" text class="text-white">
          Войти
        </v-btn>
        <v-btn to="/register" text class="text-white">
          Регистрация
        </v-btn>
      </template>
    </v-app-bar>

    <v-main>
      <router-view></router-view>
    </v-main>

    <v-footer app>
      <span>&copy; {{ new Date().getFullYear() }} — Гостевой дом</span>
    </v-footer>
  </v-app>
</template>

<style>
#app {
  font-family: 'Roboto', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

:root {
  --primary-color: #0066B3;
  --secondary-color: #FFB800;
}

.v-application {
  .primary {
    background-color: var(--primary-color) !important;
    border-color: var(--primary-color) !important;
  }
  
  .primary--text {
    color: var(--primary-color) !important;
  }
  
  .secondary {
    background-color: var(--secondary-color) !important;
    border-color: var(--secondary-color) !important;
  }
}

.v-btn {
  text-transform: none !important;
  border-radius: 8px;
}
</style>
