<template>
  <div class="login-form">
    <v-card class="mx-auto pa-6" max-width="400">
      <v-card-title class="text-center text-h5 mb-4">
        Вход в систему
      </v-card-title>

      <v-form @submit.prevent="handleSubmit" v-model="isValid">
        <v-text-field
          v-model="username"
          label="Имя пользователя"
          :rules="[rules.required]"
          prepend-icon="mdi-account"
          variant="outlined"
          class="mb-4"
        ></v-text-field>

        <v-text-field
          v-model="password"
          label="Пароль"
          :rules="[rules.required]"
          prepend-icon="mdi-lock"
          :type="showPassword ? 'text' : 'password'"
          :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
          @click:append="showPassword = !showPassword"
          variant="outlined"
          class="mb-6"
        ></v-text-field>

        <v-alert
          v-if="error"
          type="error"
          class="mb-4"
          density="compact"
        >
          {{ error }}
        </v-alert>

        <v-btn
          type="submit"
          color="primary"
          block
          :loading="loading"
          :disabled="!isValid || loading"
        >
          Войти
        </v-btn>

        <div class="text-center mt-4">
          <span class="text-body-2">Нет аккаунта? </span>
          <router-link to="/register" class="text-primary">
            Зарегистрироваться
          </router-link>
        </div>
      </v-form>
    </v-card>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'LoginForm',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const username = ref('')
    const password = ref('')
    const showPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    const isValid = ref(false)

    const rules = {
      required: value => !!value || 'Обязательное поле'
    }

    const handleSubmit = async () => {
      if (!isValid.value) return

      loading.value = true
      error.value = ''

      try {
        await authStore.login({
          username: username.value,
          password: password.value
        })
        router.push('/')
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при входе'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      password,
      showPassword,
      loading,
      error,
      isValid,
      rules,
      handleSubmit
    }
  }
}
</script>

<style scoped>
.login-form {
  max-width: 400px;
  margin: 40px auto;
  padding: 0 16px;
}
</style> 