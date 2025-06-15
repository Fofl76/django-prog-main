<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" sm="8" md="6">
        <v-card>
          <v-card-title>Бронирование комнаты</v-card-title>
          <v-card-text>
            <v-form @submit.prevent="handleSubmit">
              <v-text-field
                v-model="roomInfo.room_number"
                label="Номер комнаты"
                readonly
              ></v-text-field>
              <v-text-field
                v-model="roomInfo.price_per_night"
                label="Цена за ночь"
                readonly
                suffix="руб."
              ></v-text-field>
              <v-date-picker
                v-model="dates"
                range
                label="Даты проживания"
                required
              ></v-date-picker>
              <v-text-field
                v-model="guests"
                label="Количество гостей"
                type="number"
                :rules="[v => v <= roomInfo.max_occupancy || 'Превышено максимальное количество гостей']"
                required
              ></v-text-field>
              <v-btn
                color="primary"
                type="submit"
                block
                :loading="loading"
                :disabled="!isValid"
              >
                Забронировать
              </v-btn>
            </v-form>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'BookingForm',
  props: {
    id: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      dates: [],
      guests: 1,
      loading: false
    }
  },
  computed: {
    ...mapState(['rooms']),
    roomInfo() {
      return this.rooms.find(room => room.id === parseInt(this.id)) || {}
    },
    isValid() {
      return this.dates.length === 2 && 
             this.guests > 0 && 
             this.guests <= this.roomInfo.max_occupancy
    }
  },
  methods: {
    ...mapActions(['bookRoom', 'fetchRooms']),
    async handleSubmit() {
      if (!this.isValid) return

      this.loading = true
      try {
        await this.bookRoom({
          room: this.id,
          check_in: this.dates[0],
          check_out: this.dates[1],
          guests: this.guests
        })
        this.$router.push('/')
      } catch (error) {
        console.error('Booking error:', error)
        // Здесь можно добавить обработку ошибок
      } finally {
        this.loading = false
      }
    }
  },
  created() {
    if (!this.rooms.length) {
      this.fetchRooms()
    }
  }
}
</script> 