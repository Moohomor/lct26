<script setup lang="ts">
useHead({
  titleTemplate: (titleChunk) => {
    return titleChunk ? `${titleChunk} - Роботы для всех` : 'Роботы для всех'
  },
  meta: [
    { name: 'description', content: 'Единая платформа для подбора, сравнения и внедрения робототехнических решений в промышленности, логистике, городских сервисах и коммерческой недвижимости.' },
    { name: 'keywords', content: 'робототехника,роботы для всех,каталог роботов,AMR,промышленные роботы,автоматизация' },
    { name: 'robots', content: 'noindex, nofollow' },
  ],
})
</script>

<template>
  <NuxtLoadingIndicator />
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>