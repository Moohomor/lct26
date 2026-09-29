<script setup lang="ts">
useHead({
  title: 'Регистрация',
})

const router = useRouter();

const loginTo = () => {
    router.push('/login')
}

// ── Регистрация ────────────────────────────────────────────────────────────
const email = ref('')
const fullName = ref('')
const lastName = ref('')
const organization = ref('')
const password = ref('')
const passwordRepeat = ref('')
const agreed = ref(false)
const showPassword = ref(false)
const showPasswordRepeat = ref(false)
const loading = ref(false)
const error = ref('')

const authStore = useAuthStore()

async function submit() {
  error.value = ''

  if (!agreed.value) {
    error.value = 'Нужно согласиться с условиями и обработкой персональных данных.'
    return
  }
  if (password.value.length < 8) {
    error.value = 'Пароль должен быть не короче 8 символов.'
    return
  }
  if (password.value !== passwordRepeat.value) {
    error.value = 'Пароли не совпадают.'
    return
  }

  loading.value = true
  try {
    // Бэкенд ждёт одно поле full_name, а форма спрашивает имя и фамилию
    // отдельно. Раньше оба поля были привязаны к fullName, и фамилия
    // затирала имя: пользователь вводил «Иван», потом «Петров» — и в
    // профиль попадал только «Петров».
    const name = [fullName.value.trim(), lastName.value.trim()].filter(Boolean).join(' ')
    await authStore.register(
      email.value.trim(),
      password.value,
      name || undefined,
      organization.value.trim() || undefined,
    )
    router.push('/')
  } catch (e: any) {
    error.value = e?.data?.message ?? e?.message ?? 'Не удалось зарегистрироваться'
  } finally {
    loading.value = false
  }
}

function togglePassword(which: 'password' | 'repeat') {
  if (which === 'password') showPassword.value = !showPassword.value
  else showPasswordRepeat.value = !showPasswordRepeat.value
}
</script>

<template>
<header class="jsx-6ce8f1f93781e4d3 rg-topbar">
    <AppLogo class="rg-brand" />
        <div class="jsx-6ce8f1f93781e4d3 rg-login-link"><span class="jsx-6ce8f1f93781e4d3">Уже есть аккаунт?</span>
            <button @click="loginTo" type="button" class="jsx-6ce8f1f93781e4d3">Войти</button>
        </div>
    </header>
    <section class="jsx-6ce8f1f93781e4d3 rg-layout">
        <div class="jsx-6ce8f1f93781e4d3 rg-card">
            <div class="jsx-6ce8f1f93781e4d3 rg-card-head"><h2 class="jsx-6ce8f1f93781e4d3 rg-card-title">Создайте
                аккаунт</h2>
                <p class="jsx-6ce8f1f93781e4d3 rg-card-sub">Заполните форму для регистрации на платформе</p></div>
            <form novalidate="" @submit.prevent="submit" class="jsx-6ce8f1f93781e4d3 rg-form">
                <div class="jsx-6ce8f1f93781e4d3 rg-two-col">
                    <div class="jsx-6ce8f1f93781e4d3 rg-field">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-user rg-field-icon">
                            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        <input v-model="fullName" placeholder="Имя" autocomplete="given-name" required=""
                               class="jsx-6ce8f1f93781e4d3 rg-input" type="text"></div>
                    <div class="jsx-6ce8f1f93781e4d3 rg-field">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-user rg-field-icon">
                            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        <input v-model="lastName" placeholder="Фамилия (необязательно)" autocomplete="family-name" class="jsx-6ce8f1f93781e4d3 rg-input"
                               type="text"></div>
                </div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-mail rg-field-icon">
                        <rect width="20" height="16" x="2" y="4" rx="2"></rect>
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                    </svg>
                    <input v-model="email" type="email" placeholder="E-mail" autocomplete="email" required=""
                           class="jsx-6ce8f1f93781e4d3 rg-input"></div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-building rg-field-icon">
                        <rect width="16" height="20" x="4" y="2" rx="2"></rect>
                        <path d="M9 22v-4h6v4"></path>
                        <path d="M8 6h.01M16 6h.01M8 10h.01M16 10h.01M8 14h.01M16 14h.01"></path>
                    </svg>
                    <input v-model="organization" placeholder="Организация (необязательно)"
                           autocomplete="organization" class="jsx-6ce8f1f93781e4d3 rg-input" type="text"></div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-lock rg-field-icon">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    <input v-model="password" placeholder="Пароль" autocomplete="new-password" minlength="8" required=""
                           class="jsx-6ce8f1f93781e4d3 rg-input rg-input--pw" :type="showPassword ? 'text' : 'password'">
                    <button type="button" @click="togglePassword('password')" aria-label="Показать пароль" class="jsx-6ce8f1f93781e4d3 rg-eye">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-eye">
                            <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                    </button>
                </div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-lock rg-field-icon">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    <input v-model="passwordRepeat" placeholder="Подтвердите пароль" autocomplete="new-password" minlength="8" required=""
                           class="jsx-6ce8f1f93781e4d3 rg-input rg-input--pw" :type="showPasswordRepeat ? 'text' : 'password'">
                    <button type="button" @click="togglePassword('repeat')" aria-label="Показать пароль" class="jsx-6ce8f1f93781e4d3 rg-eye">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-eye">
                            <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                    </button>
                </div>
                <label class="jsx-6ce8f1f93781e4d3 rg-agree">
                    <button type="button" role="checkbox" :aria-checked="agreed" :data-on="agreed ? '1' : '0'"
                            aria-label="Согласие с условиями" class="jsx-6ce8f1f93781e4d3 rg-check"
                            @click="agreed = !agreed"></button>
                    <span class="jsx-6ce8f1f93781e4d3">Я согласен с <a class="rg-link"
                                                                       href="/personal-data">обработкой персональных данных</a><br
                            class="jsx-6ce8f1f93781e4d3">и принимаю условия <a class="rg-link"
                                                                               href="/terms">пользовательского соглашения</a></span></label>
                <p v-if="error" class="jsx-6ce8f1f93781e4d3 rg-error">{{ error }}</p>
                <button type="submit" :disabled="loading" class="jsx-6ce8f1f93781e4d3 rg-submit">{{
                    loading ? 'Регистрируем...' : 'Зарегистрироваться' }}</button>
                
                <p class="jsx-6ce8f1f93781e4d3 rg-legal">Нажимая «Зарегистрироваться», вы соглашаетесь<br
                        class="jsx-6ce8f1f93781e4d3">с условиями <a class="rg-link" href="/terms">пользовательского
                    соглашения</a> и <a class="rg-link" href="/privacy">политикой
                    конфиденциальности</a></p></form>
        </div>
    </section>
</template>

<style scoped>
/* Сообщение об ошибке регистрации: бэкенд отдаёт {code, message, hint},
показываем message — он уже написан для человека. */
.rg-error {
  margin: 0 0 12px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.45;
  color: #b42318;
  background: #fef3f2;
  border: 1px solid #fecdca;
  border-radius: 8px;
}

.rg-submit:disabled {
  opacity: .6;
  cursor: progress;
}
</style>
