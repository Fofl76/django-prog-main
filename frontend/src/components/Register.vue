<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>Регистрация</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="username"
                label="Имя пользователя"
                required
              ></v-text-field>
              <v-text-field
                v-model="email"
                label="Email"
                type="email"
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
                Зарегистрироваться
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
  name: 'Register',
  data() {
    return {
      username: '',
      email: '',
      password: '',
      loading: false
    }
  },
  methods: {
    ...mapActions(['register']),
    async handleSubmit() {
      this.loading = true
      try {
        await this.register({
          username: this.username,
          email: this.email,
          password: this.password
        })
        this.$router.push('/')
      } catch (error) {
        console.error('Registration error:', error)
        // Здесь можно добавить обработку ошибок
      } finally {
        this.loading = false
      }
    }
  }
}
</script> 