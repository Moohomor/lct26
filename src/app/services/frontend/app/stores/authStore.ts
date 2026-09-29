export const useAuthStore = defineStore('authStore', {
  state: () => ({
    user: null as null | {
      id: number
      email: string
      full_name: string | null
      organization: string | null
      role: 'user' | 'admin'
      is_active: boolean
    },
    token: '',
  }),
  getters: {
    isAuthenticated: (state) => !!state.token,
    isAdmin: (state) => state.user?.role === 'admin',
  },
  actions: {
    async login (email: string, password: string) {
      const { $fetchApi } = useNuxtApp()

      const res = await $fetchApi<{
        access_token: string
        refresh_token: string
        token_type: string
        expires_in: number
        user: {
          id: number
          email: string
          full_name: string | null
          organization: string | null
          role: 'user' | 'admin'
          is_active: boolean
        }
      }>('/api/v1/auth/login', {
        method: 'POST',
        body: { email, password },
      })

      this.token = res.access_token
      this.user = res.user

      // Токен храним в cookie: он отправляется браузером автоматически
      // и не доступен XSS-атакам из JS.
      const tokenCookie = useCookie('access_token', {
        maxAge: res.expires_in,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
      })
      tokenCookie.value = res.access_token
    },

    async register (email: string, password: string, fullName?: string, organization?: string) {
      const { $fetchApi } = useNuxtApp()

      const res = await $fetchApi<{
        access_token: string
        refresh_token: string
        token_type: string
        expires_in: number
        user: {
          id: number
          email: string
          full_name: string | null
          organization: string | null
          role: 'user' | 'admin'
          is_active: boolean
        }
      }>('/api/v1/auth/register', {
        method: 'POST',
        body: { email, password, full_name: fullName, organization },
      })

      this.token = res.access_token
      this.user = res.user

      const tokenCookie = useCookie('access_token', {
        maxAge: res.expires_in,
        sameSite: 'lax',
        secure: process.env.NODE_ENV === 'production',
      })
      tokenCookie.value = res.access_token
    },

    async fetchMe () {
      const { $fetchApi } = useNuxtApp()
      this.user = await $fetchApi('/api/v1/auth/me')
      this.token = useCookie('access_token').value ?? ''
    },

    logout () {
      this.user = null
      this.token = ''
      const tokenCookie = useCookie('access_token')
      tokenCookie.value = null
    },
  },
})
