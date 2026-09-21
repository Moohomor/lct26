export const useHeaderMobileMenuStore = defineStore('headerMobileMenuStore', {
  state: () => ({
    open: false,
  }),
  actions: {
    onOpen () {
        this.open = true;
    },

    onClose () {
        this.open = false;
    },
  },
})
