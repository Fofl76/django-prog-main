<template>
  <header class="header">
    <div class="logo" @click="goToMain" style="cursor:pointer;">
      <span>Гостевой Дом Приветливый</span>
    </div>
    <div class="search-bar" style="position: relative;">
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Введите номер или тип комнаты"
        @input="onInput"
        @keydown.down="highlightNext"
        @keydown.up="highlightPrev"
        @keydown.enter="onEnter"
        @blur="hideDropdown"
        @focus="onInput"
        autocomplete="off"
        style="padding: 5px 10px; border: 2px solid #007bff; border-radius: 20px; width: 200px;"
      />
      <button @click="onEnter" style="margin-left: 8px;">Найти</button>
      <ul v-if="showDropdown && filteredResults.length" class="autocomplete-list">
        <li
          v-for="(item, idx) in filteredResults"
          :key="item.id"
          :class="{ 'highlighted': idx === highlightedIndex }"
          @mousedown.prevent="selectRoom(item)"
        >
          {{ item.room_number }} — {{ item.room_type }}
        </li>
      </ul>
    </div>
    <div class="actions">
      <button @click="goToCatalog">Каталог</button>
      <button @click="goToProfile">
        <span>{{ isAuthenticated ? 'Личный кабинет' : 'Войти' }}</span>
      </button>
    </div>
  </header>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { roomsAPI } from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const isAuthenticated = computed(() => authStore.isAuthenticated)

const searchQuery = ref('')
const searchResults = ref([])
const showDropdown = ref(false)
const highlightedIndex = ref(-1)

const onInput = async () => {
  if (!searchQuery.value) {
    searchResults.value = []
    showDropdown.value = false
    return
  }
  const data = await roomsAPI.getRooms({ search: searchQuery.value })
  searchResults.value = data.results || []
  showDropdown.value = true
  highlightedIndex.value = -1
}

const filteredResults = computed(() => searchResults.value)

const selectRoom = (room) => {
  router.push(`/rooms/${room.id}`)
  searchQuery.value = ''
  showDropdown.value = false
}

const onEnter = () => {
  if (showDropdown.value && highlightedIndex.value >= 0) {
    selectRoom(filteredResults.value[highlightedIndex.value])
  } else if (filteredResults.value.length === 1) {
    selectRoom(filteredResults.value[0])
  } else if (filteredResults.value.length > 1) {
    alert('Найдено несколько номеров, уточните запрос')
  } else {
    alert('Номера не найдены')
  }
}

const highlightNext = () => {
  if (!showDropdown.value) return
  highlightedIndex.value = (highlightedIndex.value + 1) % filteredResults.value.length
}
const highlightPrev = () => {
  if (!showDropdown.value) return
  highlightedIndex.value = (highlightedIndex.value - 1 + filteredResults.value.length) % filteredResults.value.length
}
const hideDropdown = () => {
  setTimeout(() => { showDropdown.value = false }, 100)
}

const goToMain = () => {
  router.push('/')
}

const goToCatalog = () => {
  router.push('/catalog')
}

const goToProfile = () => {
  router.push('/profile')
}
</script>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #fff;
  padding: 10px 20px;
  border-bottom: 4px solid #FFCC66;
  width: 100%;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
}

.logo span {
  font-size: 24px;
  font-weight: bold;
  color: #007bff; /* Match the blue theme */
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 160px;
}

.search-bar input {
  padding: 5px 10px;
  border: 2px solid #007bff;
  border-radius: 20px;
  width: 200px;
}

.search-bar button {
  padding: 5px 15px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
}

.search-bar button:hover {
  background-color: #0056b3;
}

.actions button {
  margin-left: 10px;
  padding: 5px 15px;
  background-color: #ADD8E6; /* Light blue for buttons */
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
}

.actions button:hover {
  background-color: #87CEEB;
}

.autocomplete-list {
  position: absolute;
  top: 38px;
  left: 0;
  width: 100%;
  background: #fff;
  border: 1px solid #007bff;
  border-radius: 0 0 10px 10px;
  z-index: 1001;
  max-height: 200px;
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 0;
}
.autocomplete-list li {
  padding: 8px 16px;
  cursor: pointer;
}
.autocomplete-list li.highlighted,
.autocomplete-list li:hover {
  background: #e6f0fa;
}
</style> 