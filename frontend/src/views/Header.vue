<template>
  <header class="header">
    <div class="logo">
      <img src="../assets/img/logo.png" alt="Логотип" />
    </div>
    <div class="search-bar">
      <input type="text" placeholder="Поиск..." />
      <button>Найти</button>
    </div>
    <div class="actions">
      <button @click="goToCatalog">Каталог</button>
      <button @click="goToProfile">Личный кабинет</button>
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

.logo img {
  height: 100px;
}

.search-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-bar input {
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 4px;
}

.search-bar button {
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.search-bar button:hover {
  background-color: #0056b3;
}

.actions button {
  margin-left: 10px;
  margin-right: 50px;
  padding: 5px 10px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.actions button:hover {
  background-color: #0056b3;
}
</style>