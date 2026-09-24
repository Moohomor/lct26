export default defineNuxtRouteMiddleware((to, from) => {
  if (import.meta.client) {
    const store = useHeaderMobileMenuStore()
    store.onClose()    
  }
})
