<template>
  <header class="header">
    <div class="logo">
      <span>Гостевой Дом Приветливый</span> <!-- Replace with image or SVG if preferred -->
    </div>
    <div class="search-bar">
      <input type="text" placeholder="Двухместный номер" />
      <button>Найти</button>
    </div>
    <div class="actions">
      <button @click="goToCatalog">Каталог</button>
      <button @click="goToProfile">
        <span>Личный кабинет</span> <!-- Add user icon here if possible -->
      </button>
    </div>
  </header>
</template>

<script setup>
const goToCatalog = () => {
  console.log('Переход в каталог')
}

const goToProfile = () => {
  console.log('Переход в личный кабинет')
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
</style>