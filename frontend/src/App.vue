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
    <v-main>
      <router-view></router-view>
    </v-main>
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
