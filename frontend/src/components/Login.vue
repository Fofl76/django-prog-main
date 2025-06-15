<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>Вход в систему</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="username"
                label="Имя пользователя"
                required
              ></v-text-field>
              <v-text-field
                v-model="password"
                label="Пароль"
                type="password"
                required
              ></v-text-field>
              <v-btn
                color="primary"
                type="submit"
                block
                :loading="loading"
              >
                Войти
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      username: '',
      password: '',
      loading: false
    }
  },
  methods: {
    ...mapActions(['login']),
    async handleSubmit() {
      this.loading = true
      try {
        await this.login({
          username: this.username,
          password: this.password
        })
        this.$router.push('/')
      } catch (error) {
        console.error('Login error:', error)
        // Здесь можно добавить обработку ошибок
      } finally {
        this.loading = false
      }
    }
  }
}
</script> 