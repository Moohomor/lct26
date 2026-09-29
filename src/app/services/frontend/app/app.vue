<script setup lang="ts">
// Токен хранится в cookie, а состояние пользователя — в памяти стора.
// Без этого вызова перезагрузка страницы выглядит как выход из аккаунта.
const auth = useAuthStore()

if (useCookie('access_token').value) {
    try {
        await auth.fetchMe()
    } catch {
        // Токен протух или отозван — чистим, чтобы шапка показала вход.
        auth.logout()
    }
}

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