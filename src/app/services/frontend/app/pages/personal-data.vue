<script setup lang="ts">
useHead({ title: 'Обработка персональных данных' })

// Страницу открывает ссылка из согласия на регистрации — раньше она вела
// в 404, и согласиться с обработкой данных было нечем.
//
// Список полей взят из модели User, а не придуман: при регистрации
// отправляются ровно эти четыре значения, пароль хранится хешем.
const STORED = [
  { field: 'E-mail', why: 'Идентификатор учётной записи и вход в систему' },
  { field: 'Пароль', why: 'Хранится только в виде хеша — в открытом виде нигде не сохраняется' },
  { field: 'Имя и фамилия', why: 'Отображаются в интерфейсе и в снимках расчётов' },
  { field: 'Организация', why: 'Необязательное поле, отображается рядом с именем' },
]

const ALSO = [
  'Создаваемые проекты, сценарии и результаты расчётов — они принадлежат вашей учётной записи.',
  'Технические данные сеанса: адрес, время запросов. Нужны для диагностики сбоев.',
  'Журнал действий администраторов: кто и когда менял справочники.',
]
</script>

<template>
    <section class="relative isolate overflow-hidden" style="margin-top: -76px;">
        <div class="pd-wrap">
            <div class="pd-intro">
                <h1>Обработка персональных данных</h1>
                <p>
                    Что платформа сохраняет при регистрации и зачем это нужно. Страница
                    описывает фактическое поведение системы: список полей взят из модели
                    пользователя.
                </p>
            </div>

            <section class="pd-card">
                <h2>Поля формы регистрации</h2>
                <table class="pd-table">
                    <thead>
                    <tr>
                        <th scope="col">Поле</th>
                        <th scope="col">Зачем хранится</th>
                    </tr>
                    </thead>
                    <tbody>
                    <tr v-for="row in STORED" :key="row.field">
                        <th scope="row">{{ row.field }}</th>
                        <td>{{ row.why }}</td>
                    </tr>
                    </tbody>
                </table>
                <p class="pd-note">
                    Телефон, адрес, паспортные и платёжные данные форма не запрашивает,
                    и в базе для них нет полей.
                </p>
            </section>

            <section class="pd-card">
                <h2>Что ещё остаётся в системе</h2>
                <ul class="pd-list">
                    <li v-for="item in ALSO" :key="item">{{ item }}</li>
                </ul>
            </section>

            <section class="pd-card">
                <h2>Права и удаление</h2>
                <p class="pd-text">
                    Учётную запись можно удалить — вместе с ней удаляются созданные проекты,
                    сценарии и расчёты. Данные хранятся в базе проекта и не передаются третьим
                    лицам.
                </p>
                <p class="pd-text">
                    Это демонстрационная сборка платформы для хакатона. Юридический документ
                    об обработке персональных данных, принятый организатором, здесь не
                    публикуется: выдумывать его текст было бы неверно.
                </p>
                <NuxtLink to="/contacts" class="pd-btn">К доступу и поддержке</NuxtLink>
            </section>
        </div>
    </section>
</template>

<style scoped>
.pd-wrap { max-width: 1440px; margin: 0 auto; padding: 106px clamp(20px, 4vw, 40px) 40px; }
.pd-intro { max-width: 660px; margin-bottom: 18px; }
.pd-intro h1 { margin: 0; font-size: clamp(28px, 3.4vw, 46px); line-height: 1.05;
    letter-spacing: -0.03em; font-weight: 800; color: #0B1626; }
.pd-intro p { margin: 16px 0 0; max-width: 580px; font-size: clamp(14px, 1.4vw, 17px);
    line-height: 1.5; color: #4C586A; }

.pd-card { background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 16px; box-shadow: 0 16px 45px rgba(31, 73, 136, 0.08); backdrop-filter: blur(8px);
    padding: 18px; margin-bottom: 14px; }
.pd-card h2 { margin: 0 0 10px; font-size: 17px; color: #0B1626; }
.pd-text { margin: 0 0 10px; font-size: 12px; line-height: 1.6; color: #4C586A; }
.pd-text:last-of-type { margin-bottom: 14px; }
.pd-note { margin: 10px 0 0; padding: 9px 11px; border-radius: 10px; background: #F4F8FF;
    font-size: 11px; line-height: 1.5; color: #4C586A; }

.pd-table { width: 100%; border-collapse: collapse; font-size: 12px; }
.pd-table th, .pd-table td { padding: 8px 8px 8px 0; text-align: left; vertical-align: top;
    border-bottom: 1px solid #EDF1F7; }
.pd-table thead th { font-size: 10.5px; font-weight: 600; color: #607089; }
.pd-table tbody th { font-weight: 600; color: #0B1626; width: 30%; }
.pd-table td { color: #3C4A63; }

.pd-list { margin: 0; padding-left: 18px; font-size: 12px; line-height: 1.6; color: #4C586A; }
.pd-list li { margin-bottom: 5px; }

.pd-btn { display: inline-flex; align-items: center; height: 40px; padding: 0 18px; border-radius: 11px;
    background: var(--accent, #1E88FF); color: #fff; font-weight: 700; font-size: 13px;
    text-decoration: none; }
</style>
