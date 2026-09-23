<script setup lang="ts">
useHead({
  title: 'Регистрация',
})

const router = useRouter();

const loginTo = () => {
    router.push('/login')
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
            <form novalidate="" class="jsx-6ce8f1f93781e4d3 rg-form">
                <div class="jsx-6ce8f1f93781e4d3 rg-two-col">
                    <div class="jsx-6ce8f1f93781e4d3 rg-field">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-user rg-field-icon">
                            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        <input placeholder="Имя" autocomplete="given-name" required=""
                               class="jsx-6ce8f1f93781e4d3 rg-input" type="text"></div>
                    <div class="jsx-6ce8f1f93781e4d3 rg-field">
                        <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                             stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                             class="lucide lucide-user rg-field-icon">
                            <path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path>
                            <circle cx="12" cy="7" r="4"></circle>
                        </svg>
                        <input placeholder="Фамилия" autocomplete="family-name" class="jsx-6ce8f1f93781e4d3 rg-input"
                               type="text"></div>
                </div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-mail rg-field-icon">
                        <rect width="20" height="16" x="2" y="4" rx="2"></rect>
                        <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"></path>
                    </svg>
                    <input type="email" placeholder="E-mail" autocomplete="email" required=""
                           class="jsx-6ce8f1f93781e4d3 rg-input"></div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-phone rg-field-icon">
                        <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path>
                    </svg>
                    <input placeholder="Телефон  +7 (___) ___-__-__" autocomplete="tel"
                           class="jsx-6ce8f1f93781e4d3 rg-input" type="tel"></div>
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-lock rg-field-icon">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    <input placeholder="Пароль" autocomplete="new-password" minlength="8" required=""
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
                <div class="jsx-6ce8f1f93781e4d3 rg-field">
                    <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24" fill="none"
                         stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"
                         class="lucide lucide-lock rg-field-icon">
                        <rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect>
                        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                    </svg>
                    <input placeholder="Подтвердите пароль" autocomplete="new-password" minlength="8" required=""
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
                <label class="jsx-6ce8f1f93781e4d3 rg-agree">
                    <button type="button" role="checkbox" aria-checked="false" data-on="0"
                            aria-label="Согласие с условиями" class="jsx-6ce8f1f93781e4d3 rg-check"></button>
                    <span class="jsx-6ce8f1f93781e4d3">Я согласен с <a class="rg-link"
                                                                       href="/personal-data">обработкой персональных данных</a><br
                            class="jsx-6ce8f1f93781e4d3">и принимаю условия <a class="rg-link"
                                                                               href="/terms">пользовательского соглашения</a></span></label>
                <button type="submit" class="jsx-6ce8f1f93781e4d3 rg-submit">Зарегистрироваться</button>
                
                <p class="jsx-6ce8f1f93781e4d3 rg-legal">Нажимая «Зарегистрироваться», вы соглашаетесь<br
                        class="jsx-6ce8f1f93781e4d3">с условиями <a class="rg-link" href="/terms">пользовательского
                    соглашения</a> и <a class="rg-link" href="/privacy">политикой
                    конфиденциальности</a></p></form>
        </div>
    </section>
</template>
