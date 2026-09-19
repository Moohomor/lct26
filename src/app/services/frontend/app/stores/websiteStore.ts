export const useWebsiteStore = defineStore('websiteStore', {
  state: () => ({
    data: '',
  }),
  actions: {
    async home () {
        const { $fetchApi } = useNuxtApp()

        const res = await $fetchApi('/')

        this.data = res.Hello
    },
  },
})
