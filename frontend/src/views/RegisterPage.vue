<template>
  <div class="register-page">
    <v-container>
      <v-row justify="center" align="center" class="fill-height">
        <v-col cols="12" sm="8" md="6" lg="4">
          <v-card class="mx-auto pa-6">
            <v-card-title class="text-center text-h5 mb-4">
              Регистрация
            </v-card-title>

            <v-form @submit.prevent="handleSubmit" v-model="isValid">
              <v-text-field
                v-model="username"
                label="Имя пользователя"
                :rules="[rules.required, rules.username]"
                prepend-icon="mdi-account"
                variant="outlined"
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="email"
                label="Email"
                :rules="[rules.required, rules.email]"
                prepend-icon="mdi-email"
                variant="outlined"
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="password1"
                label="Пароль"
                :rules="[rules.required, rules.password]"
                prepend-icon="mdi-lock"
                :type="showPassword ? 'text' : 'password'"
                :append-icon="showPassword ? 'mdi-eye' : 'mdi-eye-off'"
                @click:append="showPassword = !showPassword"
                variant="outlined"
                class="mb-4"
              ></v-text-field>

              <v-text-field
                v-model="password2"
                label="Подтверждение пароля"
                :rules="[rules.required, rules.passwordMatch]"
                prepend-icon="mdi-lock-check"
                :type="showPassword ? 'text' : 'password'"
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
                Зарегистрироваться
              </v-btn>

              <div class="text-center mt-4">
                <span class="text-body-2">Уже есть аккаунт? </span>
                <router-link to="/login" class="text-primary text-decoration-none">
                  Войти
                </router-link>
              </div>
            </v-form>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'RegisterPage',
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const username = ref('')
    const email = ref('')
    const password1 = ref('')
    const password2 = ref('')
    const showPassword = ref(false)
    const loading = ref(false)
    const error = ref('')
    const isValid = ref(false)

    const rules = {
      required: value => !!value || 'Обязательное поле',
      username: value => {
        const pattern = /^[\w.@+-]+$/
        return pattern.test(value) || 'Допустимы только буквы, цифры и символы @/./+/-/_'
      },
      email: value => {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        return pattern.test(value) || 'Введите корректный email'
      },
      password: value => {
        if (value.length < 8) return 'Минимальная длина пароля 8 символов'
        if (!/\d/.test(value)) return 'Пароль должен содержать хотя бы одну цифру'
        if (!/[a-zA-Z]/.test(value)) return 'Пароль должен содержать хотя бы одну букву'
        return true
      },
      passwordMatch: value => password1.value === value || 'Пароли не совпадают'
    }

    const handleSubmit = async () => {
      if (!isValid.value) return

      loading.value = true
      error.value = ''

      try {
        await authStore.register({
          username: username.value,
          email: email.value,
          password1: password1.value,
          password2: password2.value
        })
        router.push('/login')
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при регистрации'
      } finally {
        loading.value = false
      }
    }

    return {
      username,
      email,
      password1,
      password2,
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
.register-page {
  min-height: calc(100vh - 64px); /* Высота экрана минус высота header */
}
</style> 