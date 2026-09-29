<script setup lang="ts">
useHead({ title: 'Контакты и доступ' })

// Страницу открывают ссылки из карточки «Поддержка» на главной и из
// подвала — раньше обе вели в 404.
//
// Контактов организатора здесь нет: телефон и почту выдумывать нельзя,
// это была бы чужая вымышленная организация. Вместо этого страница
// отвечает на вопрос, с которым к ней и приходят на демонстрации: как
// попасть в платформу и что в ней посмотреть.
const auth = useAuthStore()

const CAPABILITIES = [
  {
    to: '/catalog',
    title: 'Каталог решений',
    text: 'Позиции с фотографиями, ценами и характеристиками из каталога внедрения ФЦ БАС.',
  },
  {
    to: '/financing',
    title: 'Расчёт экономики',
    text: 'Стоимость владения, окупаемость и чувствительность к допущениям под параметры объекта.',
  },
  {
    to: '/cases',
    title: 'Кейсы внедрения',
    text: 'Что уже эксплуатируется: техника, отрасли, регионы, уровень готовности.',
  },
  {
    to: '/pilot-testing',
    title: 'Пилотирование',
    text: 'Решения, которые сейчас проходят пилот, с распределением по уровню готовности.',
  },
]
</script>

<template>
    <section class="relative isolate overflow-hidden" style="margin-top: -76px;">
        <div class="ct-wrap">
            <div class="ct-intro">
                <h1>Доступ и возможности платформы</h1>
                <p>
                    Платформа открыта для просмотра: каталог, кейсы и пилотирование доступны
                    без входа. Расчёт экономики и подбор требуют аккаунта — вход занимает
                    секунду по демонстрационным учётным записям.
                </p>
            </div>

            <section class="ct-card ct-card--demo">
                <h2>Демонстрационный доступ</h2>
                <p class="ct-hint">
                    Учётные записи созданы при наполнении базы и подходят для показа.
                    Свою учётную запись можно завести на странице регистрации.
                </p>
                <div class="ct-creds">
                    <div class="ct-cred">
                        <span>Пользователь</span>
                        <code>user@example.com</code>
                    </div>
                    <div class="ct-cred">
                        <span>Пароль</span>
                        <code>demo12345</code>
                    </div>
                    <div class="ct-cred">
                        <span>Администратор</span>
                        <code>admin@example.com</code>
                    </div>
                </div>
                <div class="ct-actions">
                    <NuxtLink v-if="!auth.isAuthenticated" to="/login" class="ct-btn">Войти</NuxtLink>
                    <NuxtLink v-if="!auth.isAuthenticated" to="/register" class="ct-btn ct-btn--ghost">
                        Зарегистрироваться
                    </NuxtLink>
                    <NuxtLink v-else to="/financing" class="ct-btn">Перейти к расчёту</NuxtLink>
                </div>
            </section>

            <section class="ct-card">
                <h2>Что можно посмотреть</h2>
                <ul class="ct-list">
                    <li v-for="c in CAPABILITIES" :key="c.to">
                        <NuxtLink :to="c.to">
                            <b>{{ c.title }}</b>
                            <span>{{ c.text }}</span>
                        </NuxtLink>
                    </li>
                </ul>
            </section>

            <section class="ct-card">
                <h2>Откуда данные</h2>
                <p class="ct-hint">
                    Каталог решений, параметры объектов и цены взяты из датасета и каталога
                    внедрения ФЦ БАС. Экономика считается на этих данных по прозрачной модели:
                    допущения перечислены в ответе расчёта, а чувствительность показывает,
                    насколько результат зависит от каждого из них.
                </p>
                <p class="ct-hint">
                    Оценки экономии, окупаемости и сроков в каталоге не хранятся: каждый
                    расчёт зависит от параметров конкретного объекта, поэтому их считает
                    калькулятор, а не карточка позиции.
                </p>
            </section>
        </div>
    </section>
</template>

<style scoped>
.ct-wrap { max-width: 1440px; margin: 0 auto; padding: 106px clamp(20px, 4vw, 40px) 40px; }
.ct-intro { max-width: 640px; margin-bottom: 18px; }
.ct-intro h1 { margin: 0; font-size: clamp(28px, 3.4vw, 46px); line-height: 1.05;
    letter-spacing: -0.03em; font-weight: 800; color: #0B1626; }
.ct-intro p { margin: 16px 0 0; max-width: 580px; font-size: clamp(14px, 1.4vw, 17px);
    line-height: 1.5; color: #4C586A; }

.ct-card { background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 16px; box-shadow: 0 16px 45px rgba(31, 73, 136, 0.08); backdrop-filter: blur(8px);
    padding: 18px; margin-bottom: 14px; }
.ct-card h2 { margin: 0 0 4px; font-size: 17px; color: #0B1626; }
.ct-hint { margin: 0 0 10px; font-size: 12px; line-height: 1.55; color: #4C586A; }
.ct-hint:last-child { margin-bottom: 0; }

.ct-creds { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px;
    margin-bottom: 14px; }
.ct-cred { padding: 10px 12px; border: 1px solid #EDF1F7; border-radius: 11px; background: #FAFCFF; }
.ct-cred span { display: block; font-size: 10.5px; color: #607089; margin-bottom: 3px; }
.ct-cred code { font-size: 12.5px; color: #0B1626; font-weight: 600; }

.ct-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.ct-btn { display: inline-flex; align-items: center; height: 40px; padding: 0 18px; border-radius: 11px;
    background: var(--accent, #1E88FF); color: #fff; font-weight: 700; font-size: 13px;
    text-decoration: none; }
.ct-btn--ghost { background: transparent; color: #0568FF; border: 1px solid #1E88FF; }

.ct-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 9px;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); }
.ct-list a { display: block; height: 100%; padding: 12px 13px; border: 1px solid #EDF1F7;
    border-radius: 12px; background: #FBFDFF; text-decoration: none; color: inherit;
    transition: transform .2s, box-shadow .2s; }
.ct-list a:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(38, 69, 118, .12); }
.ct-list b { display: block; font-size: 13px; color: #0B1626; margin-bottom: 3px; }
.ct-list span { font-size: 11.5px; line-height: 1.45; color: #4C586A; }
</style>
