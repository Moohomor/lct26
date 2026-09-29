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
      //
      // Тело берём из response._data: ofetch к моменту вызова хука уже
      // разобрал ответ и положил его туда, а поток чтения израсходован.
      // Повторный response.json() на израсходованном потоке падает, catch
      // глушит исключение, и в форму приходил H3Error с пустым message и
      // null в data — пользователь видел пустую страницу вместо
      // «пароль не должен состоять только из букв». Разбор _data — источник
      // истины, response.json() оставлен запасным путём.
      const parsed = response._data
      const body: any =
        parsed ?? (typeof response.json === 'function' ? await response.json().catch(() => null) : null)

      // FastAPI для части ошибок отдаёт голый {detail: [...]} без обёртки —
      // такое сообщение тоже нужно показать, а не превратить в пустую строку.
      const message =
        body?.message ||
        (Array.isArray(body?.detail) ? body.detail[0]?.msg : body?.detail) ||
        response.statusMessage ||
        ''

      throw createError({
        statusCode: response.status,
        statusMessage: message,
        message,
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