// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],

  css: [
    '~/assets/css/font-face.css',
    '~/assets/css/app.css',
    '~/assets/css/footer.css',
  ],

  routeRules: {
    '/login': { 
      appLayout: 'auth'
    },
    '/register': { 
      appLayout: 'auth'
    },
  },

  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,

  // Nuxt читает переменные окружения только для ключей, объявленных здесь.
  // Без этого блока NUXT_PUBLIC_API_BASE игнорировался бы, и задеплоенный
  // фронтенд всегда ходил бы на http://localhost:5000.
  runtimeConfig: {
    public: {
      // Локально адрес задаёт docker-compose (api слушает 5000),
      // на Render — переменная NUXT_PUBLIC_API_BASE.
      apiBase: 'http://localhost:5000',
    },
  },

})