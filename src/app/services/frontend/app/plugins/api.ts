export default defineNuxtPlugin((nuxtApp) => {
  // Адрес бэкенда задаётся переменной окружения NUXT_PUBLIC_API_BASE.
  // По умолчанию — порт из docker-compose: api-сервис слушает 5000.
  const baseURL = useRuntimeConfig().public.apiBase ?? 'http://localhost:5000'

  const fetchApi = $fetch.create({
    baseURL,
    onRequest ({ options }) {
      // Токен берётся из cookie, а не из localStorage: cookie отправляется
      // браузером автоматически и не доступен XSS.
      const token = useCookie('access_token')
      if (token.value) {
        options.headers = {
          ...options.headers,
          Authorization: `Bearer ${token.value}`,
        }
      }
    },
    async onResponseError ({ response }) {
      // Единая обработка ошибок: бэкенд отдаёт {code, message, hint},
      // и пользователю нужно показать именно это, а не текст HTTP-статуса.
      const body = await response.json().catch(() => null)
      throw createError({
        statusCode: response.status,
        statusMessage: body?.message ?? response.statusMessage,
        message: body?.message ?? response.statusMessage,
        data: body,
      })
    },
  })

  return {
    provide: {
      fetchApi,
    },
  }
})