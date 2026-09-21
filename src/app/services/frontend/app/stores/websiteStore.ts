export const useWebsiteStore = defineStore('websiteStore', {
  state: () => ({
    example: '',
  }),
  actions: {
    async home () {
        const { $fetchApi } = useNuxtApp()

        const res = await $fetchApi('/')

        this.example = res
    },
  },
})
