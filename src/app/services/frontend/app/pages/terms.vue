<script setup lang="ts">
useHead({ title: 'Условия использования' })

// Ссылка из согласия на регистрации вела в 404. Текст описывает, как
// платформа устроена на самом деле, без выдуманных юридических
// формулировок: условия, принятые организатором, публикуются отдельно.
</script>

<template>
    <section class="relative isolate overflow-hidden" style="margin-top: -76px;">
        <div class="tm-wrap">
            <div class="tm-intro">
                <h1>Условия использования платформы</h1>
                <p>
                    Демонстрационная сборка для хакатона. Ниже — как платформа работает
                    и какие данные показывает.
                </p>
            </div>

            <section class="tm-card">
                <h2>Что считает платформа</h2>
                <p class="tm-text">
                    Экономика решения — покупка, RaaS и вариант без роботов — считается по
                    ценам каталога и справочнику параметров объекта. В ответе расчёта
                    перечислены все допущения модели, а анализ чувствительности показывает,
                    насколько результат зависит от каждого из них.
                </p>
                <p class="tm-text">
                    Допущения — оценочные и требуют подтверждения коммерческим предложением.
                    Расчёт не является офертой и не заменяет проектные работы.
                </p>
            </section>

            <section class="tm-card">
                <h2>Данные каталога</h2>
                <p class="tm-text">
                    Позиции, фотографии, цены и параметры объектов взяты из каталога внедрения
                    ФЦ БАС и датасета хакатона. Полнота заполнения у позиций разная: у части
                    не подтверждена ёмкость аккумулятора, у части не заполнены технические
                    характеристики. Такие позиции помечены прямо на странице.
                </p>
            </section>

            <section class="tm-card">
                <h2>Учётные записи</h2>
                <p class="tm-text">
                    Регистрация открыта, учётные записи удаляются вместе с созданными
                    проектами и расчётами. Состав хранимых полей описан на странице
                    обработки персональных данных.
                </p>
                <div class="tm-actions">
                    <NuxtLink to="/personal-data" class="tm-btn tm-btn--ghost">
                        Обработка персональных данных
                    </NuxtLink>
                    <NuxtLink to="/contacts" class="tm-btn">К доступу и поддержке</NuxtLink>
                </div>
            </section>
        </div>
    </section>
</template>

<style scoped>
.tm-wrap { max-width: 1440px; margin: 0 auto; padding: 106px clamp(20px, 4vw, 40px) 40px; }
.tm-intro { max-width: 640px; margin-bottom: 18px; }
.tm-intro h1 { margin: 0; font-size: clamp(28px, 3.4vw, 46px); line-height: 1.05;
    letter-spacing: -0.03em; font-weight: 800; color: #0B1626; }
.tm-intro p { margin: 16px 0 0; max-width: 560px; font-size: clamp(14px, 1.4vw, 17px);
    line-height: 1.5; color: #4C586A; }

.tm-card { background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 16px; box-shadow: 0 16px 45px rgba(31, 73, 136, 0.08); backdrop-filter: blur(8px);
    padding: 18px; margin-bottom: 14px; }
.tm-card h2 { margin: 0 0 10px; font-size: 17px; color: #0B1626; }
.tm-text { margin: 0 0 10px; font-size: 12px; line-height: 1.6; color: #4C586A; }
.tm-text:last-of-type { margin-bottom: 0; }

.tm-actions { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 14px; }
.tm-btn { display: inline-flex; align-items: center; height: 40px; padding: 0 18px; border-radius: 11px;
    background: var(--accent, #1E88FF); color: #fff; font-weight: 700; font-size: 13px;
    text-decoration: none; }
.tm-btn--ghost { background: transparent; color: #0568FF; border: 1px solid #1E88FF; }
</style>
