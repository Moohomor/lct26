<script setup lang="ts">
useHead({
  title: 'Вход в личный кабинет',
})

const router = useRouter();

const registerTo = () => {
    router.push('/register')
}

// ── Вход ────────────────────────────────────────────────────────────────────
const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const authStore = useAuthStore()

async function submit() {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(email.value, password.value)
    router.push('/')
  } catch (e: any) {
    // Бэкенд отдаёт {code, message, hint} — показываем сообщение и подсказку
    error.value = e?.data?.message ?? e?.message ?? 'Не удалось войти'
  } finally {
    loading.value = false
  }
}
</script>

<template>
<header class="jsx-6ce8f1f93781e4d3 rg-topbar">
    <AppLogo class="rg-brand" />
        <div class="jsx-6ce8f1f93781e4d3 rg-login-link"><span class="jsx-6ce8f1f93781e4d3">Нет аккаунта?</span>
            <button @click="registerTo" type="button" class="jsx-6ce8f1f93781e4d3">Регистрация</button>
        </div>
    </header>
    <section class="jsx-6ce8f1f93781e4d3 rg-layout">
        <div class="jsx-6ce8f1f93781e4d3 rg-card">
            <div class="jsx-6ce8f1f93781e4d3 rg-card-head"><h2 class="jsx-6ce8f1f93781e4d3 rg-card-title">Вход в
                аккаунт</h2>
                <p class="jsx-6ce8f1f93781e4d3 rg-card-sub">Войдите, чтобы продолжить работу на платформе</p></div>
            <form @submit.prevent="submit" class="jsx-6ce8f1f93781e4d3 rg-form">
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-mail rg-field-icon">
                        <rect width="20" height="16" x="2" y="4" rx="2"></rect>
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                    </svg>
                    <input v-model="email" placeholder="E-mail" autocomplete="email" required class="jsx-6ce8f1f93781e4d3 rg-input"
                           type="email"></div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-lock rg-field-icon">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    <input v-model="password" placeholder="Пароль" autocomplete="current-password" required
                           class="jsx-6ce8f1f93781e4d3 rg-input rg-input--pw" :type="showPassword ? 'text' : 'password'">
                    <button type="button" aria-label="Показать пароль" class="jsx-6ce8f1f93781e4d3 rg-eye" @click="showPassword = !showPassword">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-eye">
                            <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                    </button>
                </div>
                <p v-if="error" style="color: #dc2626; font-size: 0.875rem; margin: 0 0 8px;">{{ error }}</p>
                <button type="submit" :disabled="loading" style="margin-top: 8px;" class="jsx-6ce8f1f93781e4d3 rg-submit">
                    {{ loading ? 'Вход...' : 'Войти' }}
                </button>
                <p class="jsx-6ce8f1f93781e4d3 rg-switch">Нет аккаунта?
                    <button @click="registerTo" type="button" class="jsx-6ce8f1f93781e4d3 rg-switch-btn">Зарегистрироваться</button>
                </p>
            </form>
        </div>
    </section>
</template>
