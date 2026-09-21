// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@pinia/nuxt'],

  css: [
    '~/assets/css/font-face.css',
    '~/assets/css/app.css',
    '~/assets/css/footer.css',
  ],

  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  ssr: false,

})