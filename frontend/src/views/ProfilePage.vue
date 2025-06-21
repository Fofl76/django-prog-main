<template>
  <div class="profile-page">
    <v-container>
      <v-row justify="center">
        <v-col cols="12" md="8">
          <v-card class="pa-6">
            <v-card-title class="text-h4 mb-6">
              {{ isAuthenticated ? 'Личный кабинет' : 'Вход в систему' }}
            </v-card-title>

            <!-- Форма входа/регистрации для неавторизованных пользователей -->
            <template v-if="!isAuthenticated">
              <v-tabs v-model="authTab" class="mb-6">
                <v-tab value="login">Вход</v-tab>
                <v-tab value="register">Регистрация</v-tab>
              </v-tabs>

              <v-window v-model="authTab">
                <!-- Форма входа -->
                <v-window-item value="login">
                  <v-form @submit.prevent="handleLogin" v-model="isLoginValid">
                    <v-text-field
                      v-model="loginForm.email"
                      label="Email"
                      :rules="[rules.required, rules.email]"
                      variant="outlined"
                    ></v-text-field>
                    <v-text-field
                      v-model="loginForm.password"
                      label="Пароль"
                      type="password"
                      :rules="[rules.required]"
                      variant="outlined"
                    ></v-text-field>
                    <v-alert
                      v-if="authMessage"
                      :type="authMessageType"
                      class="mb-4"
                    >
                      {{ authMessage }}
                    </v-alert>
                    <v-btn
                      type="submit"
                      color="primary"
                      :loading="loading"
                      :disabled="!isLoginValid || loading"
                      block
                    >
                      Войти
                    </v-btn>
                  </v-form>
                </v-window-item>

                <!-- Форма регистрации -->
                <v-window-item value="register">
                  <v-form @submit.prevent="handleRegister" v-model="isRegisterValid">
                    <v-text-field
                      v-model="registerForm.email"
                      label="Email"
                      :rules="[rules.required, rules.email]"
                      variant="outlined"
                    ></v-text-field>
                    <v-text-field
                      v-model="registerForm.password"
                      label="Пароль"
                      type="password"
                      :rules="[rules.required, rules.password]"
                      variant="outlined"
                    ></v-text-field>
                    <v-text-field
                      v-model="registerForm.passwordConfirm"
                      label="Подтверждение пароля"
                      type="password"
                      :rules="[rules.required, rules.passwordMatch]"
                      variant="outlined"
                    ></v-text-field>
                    <v-alert
                      v-if="authMessage"
                      :type="authMessageType"
                      class="mb-4"
                    >
                      {{ authMessage }}
                    </v-alert>
                    <v-btn
                      type="submit"
                      color="primary"
                      :loading="loading"
                      :disabled="!isRegisterValid || loading"
                      block
                    >
                      Зарегистрироваться
                    </v-btn>
                  </v-form>
                </v-window-item>
              </v-window>
            </template>

            <!-- Контент для авторизованных пользователей -->
            <template v-else>
              <v-tabs v-model="activeTab" class="mb-6">
                <v-tab value="profile">Профиль</v-tab>
                <v-tab value="bookings">Мои бронирования</v-tab>
                <v-tab value="reviews">Мои отзывы</v-tab>
              </v-tabs>

              <v-window v-model="activeTab">
                <!-- Вкладка профиля -->
                <v-window-item value="profile">
                  <v-form @submit.prevent="updateProfile" v-model="isValid">
                    <v-row>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="profile.first_name"
                          label="Имя"
                          :rules="[rules.required]"
                          variant="outlined"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="profile.last_name"
                          label="Фамилия"
                          :rules="[rules.required]"
                          variant="outlined"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="profile.email"
                          label="Email"
                          :rules="[rules.required, rules.email]"
                          variant="outlined"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12" md="6">
                        <v-text-field
                          v-model="profile.phone_number"
                          label="Телефон"
                          :rules="[rules.required]"
                          variant="outlined"
                        ></v-text-field>
                      </v-col>
                      <v-col cols="12">
                        <v-alert
                          v-if="profileMessage"
                          :type="profileMessageType"
                          class="mb-4"
                        >
                          {{ profileMessage }}
                        </v-alert>
                        <v-btn
                          type="submit"
                          color="primary"
                          :loading="loading"
                          :disabled="!isValid || loading"
                        >
                          Сохранить изменения
                        </v-btn>
                      </v-col>
                    </v-row>
                  </v-form>
                </v-window-item>

                <!-- Вкладка бронирований -->
                <v-window-item value="bookings">
                  <v-data-table
                    :headers="bookingHeaders"
                    :items="bookings"
                    :loading="loading"
                    class="elevation-1"
                  >
                    <template #[`item.status`]="{ item }">
                      <v-chip
                        :color="getStatusColor(item.status)"
                        size="small"
                      >
                        {{ item.status }}
                      </v-chip>
                    </template>
                  </v-data-table>
                </v-window-item>

                <!-- Вкладка отзывов -->
                <v-window-item value="reviews">
                  <v-data-table
                    :headers="reviewHeaders"
                    :items="reviews"
                    :loading="loading"
                    class="elevation-1"
                  >
                    <template #[`item.rating`]="{ item }">
                      <v-rating
                        v-model="item.rating"
                        readonly
                        dense
                        color="amber"
                        background-color="grey lighten-1"
                        half-increments
                      ></v-rating>
                    </template>
                  </v-data-table>
                </v-window-item>
              </v-window>
            </template>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import axios from 'axios'

export default {
  name: 'ProfilePage',
  setup() {
    const authStore = useAuthStore()
    const router = useRouter()
    const activeTab = ref('profile')
    const authTab = ref('login')
    const loading = ref(false)
    const isValid = ref(false)
    const profileMessage = ref('')
    const profileMessageType = ref('success')
    const isLoginValid = ref(false)
    const isRegisterValid = ref(false)
    const authMessage = ref('')
    const authMessageType = ref('success')

    const isAuthenticated = computed(() => authStore.isAuthenticated)

    const profile = ref({
      first_name: '',
      last_name: '',
      email: '',
      phone_number: ''
    })

    const bookings = ref([])
    const reviews = ref([])

    const bookingHeaders = [
      { title: 'Номер', key: 'room_number' },
      { title: 'Дата заезда', key: 'check_in' },
      { title: 'Дата выезда', key: 'check_out' },
      { title: 'Статус', key: 'status' },
      { title: 'Сумма', key: 'total_price' }
    ]

    const reviewHeaders = [
      { title: 'Номер', key: 'room_number' },
      { title: 'Оценка', key: 'rating' },
      { title: 'Комментарий', key: 'comment' },
      { title: 'Дата', key: 'review_date' }
    ]

    const rules = {
      required: value => !!value || 'Обязательное поле',
      email: value => {
        const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
        return pattern.test(value) || 'Введите корректный email'
      },
      password: value => value.length >= 8 || 'Пароль должен содержать минимум 8 символов',
      passwordMatch: value => value === registerForm.value.password || 'Пароли не совпадают'
    }

    const getStatusColor = (status) => {
      const colors = {
        'confirmed': 'success',
        'pending': 'warning',
        'cancelled': 'error'
      }
      return colors[status] || 'grey'
    }

    const fetchProfile = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/profile/')
        profile.value = response.data
      } catch (error) {
        console.error('Ошибка при загрузке профиля:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchBookings = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/bookings/my/')
        bookings.value = response.data
      } catch (error) {
        console.error('Ошибка при загрузке бронирований:', error)
      } finally {
        loading.value = false
      }
    }

    const fetchReviews = async () => {
      try {
        loading.value = true
        const response = await axios.get('/api/reviews/my/')
        reviews.value = response.data
      } catch (error) {
        console.error('Ошибка при загрузке отзывов:', error)
      } finally {
        loading.value = false
      }
    }

    const updateProfile = async () => {
      try {
        loading.value = true
        await axios.put('/api/profile/', profile.value)
        profileMessage.value = 'Профиль успешно обновлен'
        profileMessageType.value = 'success'
      } catch (error) {
        profileMessage.value = 'Ошибка при обновлении профиля'
        profileMessageType.value = 'error'
        console.error('Ошибка при обновлении профиля:', error)
      } finally {
        loading.value = false
      }
    }

    const handleLogin = async () => {
      try {
        loading.value = true
        await authStore.login(loginForm.value)
        authMessage.value = 'Успешный вход'
        authMessageType.value = 'success'
        router.push('/profile')
      } catch (error) {
        authMessage.value = error.response?.data?.detail || 'Ошибка при входе'
        authMessageType.value = 'error'
      } finally {
        loading.value = false
      }
    }

    const handleRegister = async () => {
      try {
        loading.value = true
        await authStore.register(registerForm.value)
        authMessage.value = 'Регистрация успешна'
        authMessageType.value = 'success'
        router.push('/profile')
      } catch (error) {
        authMessage.value = error.response?.data?.detail || 'Ошибка при регистрации'
        authMessageType.value = 'error'
      } finally {
        loading.value = false
      }
    }

    onMounted(() => {
      fetchProfile()
      fetchBookings()
      fetchReviews()
    })

    return {
      activeTab,
      authTab,
      isAuthenticated,
      profile,
      bookings,
      reviews,
      loading,
      isValid,
      rules,
      profileMessage,
      profileMessageType,
      bookingHeaders,
      reviewHeaders,
      getStatusColor,
      updateProfile,
      isLoginValid,
      isRegisterValid,
      loginForm,
      registerForm,
      authMessage,
      authMessageType,
      handleLogin,
      handleRegister
    }
  }
}
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 64px);
  padding-top: 2rem;
}

.v-form {
  max-width: 400px;
  margin: 0 auto;
}
</style> 