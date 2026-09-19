<script setup lang="ts">

const store = useWebsiteStore()

const update = async () => { // по запросу
    await callOnce(store.home)
    
}

//onMounted(update)
</script>

<template>
  <NuxtLink to="/about">О нас</NuxtLink>
  <h1>Главная</h1>  
</template>
