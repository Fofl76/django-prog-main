<template>
  <v-container>
    <v-row>
      <v-col v-for="room in rooms" :key="room.id" cols="12" md="4">
        <v-card>
          <v-card-title>{{ room.room_number }}</v-card-title>
          <v-card-text>
            <p>Тип: {{ room.room_type }}</p>
            <p>Цена за ночь: {{ room.price_per_night }} руб.</p>
            <p>Максимальное количество гостей: {{ room.max_occupancy }}</p>
            <div v-if="room.amenities.length">
              <p>Удобства:</p>
              <v-chip v-for="amenity in room.amenities" 
                     :key="amenity.id" 
                     class="ma-1">
                {{ amenity.name }}
              </v-chip>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-btn color="primary" @click="bookRoom(room.id)">
              Забронировать
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'RoomList',
  computed: {
    ...mapState(['rooms'])
  },
  methods: {
    ...mapActions(['fetchRooms']),
    bookRoom(roomId) {
      this.$router.push(`/book/${roomId}`)
    }
  },
  created() {
    this.fetchRooms()
  }
}
</script> 