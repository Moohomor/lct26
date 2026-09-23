<script setup lang="ts">
useHead({
  title: 'Вход в личный кабинет',
})

const router = useRouter();

const registerTo = () => {
    router.push('/register')
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
            <form novalidate="" class="jsx-6ce8f1f93781e4d3 rg-form">
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-mail rg-field-icon">
                        <rect width="20" height="16" x="2" y="4" rx="2"></rect>
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                    </svg>
                    <input placeholder="E-mail" autocomplete="email" required="" class="jsx-6ce8f1f93781e4d3 rg-input"
                           type="email"></div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-lock rg-field-icon">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    <input placeholder="Пароль" autocomplete="current-password" required=""
                           class="jsx-6ce8f1f93781e4d3 rg-input rg-input--pw" type="password" value="">
                    <button type="button" aria-label="Показать пароль" class="jsx-6ce8f1f93781e4d3 rg-eye">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-eye">
                            <path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path>
                            <circle cx="12" cy="12" r="3"></circle>
                        </svg>
                    </button>
                </div>
                <button type="submit" style="margin-top: 8px;" class="jsx-6ce8f1f93781e4d3 rg-submit">Войти</button>
                <p class="jsx-6ce8f1f93781e4d3 rg-switch">Нет аккаунта?
                    <button @click="registerTo" type="button" class="jsx-6ce8f1f93781e4d3 rg-switch-btn">Зарегистрироваться</button>
                </p>
            </form>
        </div>
    </section>
</template>
