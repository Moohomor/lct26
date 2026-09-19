export default defineNuxtPlugin((nuxtApp) => {

  const fetchApi = $fetch.create({
    baseURL: 'http://localhost:5000',
    onRequest ({ request, options, error }) {
      
    },
    async onResponseError ({ response }) {
      
    },
    
  })

  // Предоставляем в useNuxtApp().$api
  return {
    provide: {
      fetchApi,
    },
  }
})