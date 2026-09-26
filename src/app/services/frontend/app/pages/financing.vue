<script setup lang="ts">
useHead({
  title: 'Финансирование роботизации',
})
</script>

<template>
    <section class="relative isolate overflow-hidden" style="margin-top: -76px;">
            <div class="mx-auto fin-dash-wrap" style="max-width: 1440px; padding: 106px clamp(20px, 4vw, 40px) 40px;">
                <div style="max-width: 620px; margin-bottom: 14px;">
                    <h1 style="display: block; margin: 0px; font-size: clamp(30px, 3.6vw, 52px); line-height: 1.05; letter-spacing: -0.03em; font-weight: 800; color: rgb(11, 22, 38);">
                        Подберём оптимальное финансирование для проекта</h1>
                    <p style="display: block; margin: 16px 0px 0px; max-width: 540px; font-size: clamp(14px, 1.4vw, 17px); line-height: 1.5; color: rgb(76, 88, 106);">
                        Сравним покупку, лизинг, аренду и RaaS. Рассчитаем платежи и подберём схему вместе с
                        банками-партнёрами.</p></div>
                <div class="fin-dash-grid">
                    <div class="fin-area-left">
                        <div class="fin-area-schemes"
                             style="background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1); border-radius: 16px; box-shadow: rgba(31, 73, 136, 0.08) 0px 16px 45px; backdrop-filter: blur(8px); padding: 16px;">
                            <p style="font-size: 13px; font-weight: 700; color: rgb(11, 22, 38); margin: 0px 0px 8px;">
                                Доступные схемы финансирования</p>
                            <div class="fin-schemes-inner">
                                <article class="fin-scheme-mini">
                                    <div style="position: relative; height: 96px; margin-bottom: 8px;"><img
                                            alt="Покупка" loading="lazy" decoding="async" data-nimg="fill"
                                            style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent; mix-blend-mode: multiply;"
                                            sizes="180px"
                                            srcset="~assets/img/buy_015.avif 16w, ~assets/img/buy_004.avif 32w, ~assets/img/buy_005.avif 48w, ~assets/img/buy_009.avif 64w, ~assets/img/buy_010.avif 96w, ~assets/img/buy_008.avif 128w, ~assets/img/buy_013.avif 256w, ~assets/img/buy.avif 384w, ~assets/img/buy_014.avif 640w, ~assets/img/buy_016.avif 750w, ~assets/img/buy_006.avif 828w, ~assets/img/buy_011.avif 1080w, ~assets/img/buy_003.avif 1200w, ~assets/img/buy_012.avif 1920w, ~assets/img/buy_007.avif 2048w, ~assets/img/buy_002.avif 3840w"
                                            src="~assets/img/buy_002.avif"></div>
                                    <h3 style="font-size: 13.5px; font-weight: 700; margin: 0px 0px 2px; color: rgb(11, 22, 38);">
                                        Покупка</h3>
                                    <p style="font-size: 10.5px; line-height: 1.35; color: rgb(76, 88, 106); margin: 0px 0px 6px;">
                                        Полное владение сразу</p>
                                    <ul style="list-style: none; padding: 0px; margin: 0px; display: grid; gap: 3px;">
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Актив на
                                            балансе
                                        </li>
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Единый
                                            платёж
                                        </li>
                                    </ul>
                                </article>
                                <article class="fin-scheme-mini">
                                    <div style="position: relative; height: 96px; margin-bottom: 8px;"><img alt="Лизинг"
                                                                                                            loading="lazy"
                                                                                                            decoding="async"
                                                                                                            data-nimg="fill"
                                                                                                            style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent; mix-blend-mode: multiply;"
                                                                                                            sizes="180px"
                                                                                                            srcset="~assets/img/lease_010.avif 16w, ~assets/img/lease_013.avif 32w, ~assets/img/lease_011.avif 48w, ~assets/img/lease_014.avif 64w, ~assets/img/lease_015.avif 96w, ~assets/img/lease_002.avif 128w, ~assets/img/lease_003.avif 256w, ~assets/img/lease.avif 384w, ~assets/img/lease_006.avif 640w, ~assets/img/lease_007.avif 750w, ~assets/img/lease_012.avif 828w, ~assets/img/lease_008.avif 1080w, ~assets/img/lease_005.avif 1200w, ~assets/img/lease_016.avif 1920w, ~assets/img/lease_004.avif 2048w, ~assets/img/lease_009.avif 3840w"
                                                                                                            src="~assets/img/lease_009.avif">
                                    </div>
                                    <h3 style="font-size: 13.5px; font-weight: 700; margin: 0px 0px 2px; color: rgb(11, 22, 38);">
                                        Лизинг</h3>
                                    <p style="font-size: 10.5px; line-height: 1.35; color: rgb(76, 88, 106); margin: 0px 0px 6px;">
                                        Финансирование от партнёров</p>
                                    <ul style="list-style: none; padding: 0px; margin: 0px; display: grid; gap: 3px;">
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Гибкий
                                            график
                                        </li>
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Аванс от
                                            10%
                                        </li>
                                    </ul>
                                </article>
                                <article class="fin-scheme-mini">
                                    <div style="position: relative; height: 96px; margin-bottom: 8px;"><img alt="Аренда"
                                                                                                            loading="lazy"
                                                                                                            decoding="async"
                                                                                                            data-nimg="fill"
                                                                                                            style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent; mix-blend-mode: multiply;"
                                                                                                            sizes="180px"
                                                                                                            srcset="~assets/img/rent_005.avif 16w, ~assets/img/rent_010.avif 32w, ~assets/img/rent_007.avif 48w, ~assets/img/rent_003.avif 64w, ~assets/img/rent_011.avif 96w, ~assets/img/rent_016.avif 128w, ~assets/img/rent_004.avif 256w, ~assets/img/rent.avif 384w, ~assets/img/rent_009.avif 640w, ~assets/img/rent_006.avif 750w, ~assets/img/rent_008.avif 828w, ~assets/img/rent_014.avif 1080w, ~assets/img/rent_012.avif 1200w, ~assets/img/rent_015.avif 1920w, ~assets/img/rent_013.avif 2048w, ~assets/img/rent_002.avif 3840w"
                                                                                                            src="~assets/img/rent_002.avif">
                                    </div>
                                    <h3 style="font-size: 13.5px; font-weight: 700; margin: 0px 0px 2px; color: rgb(11, 22, 38);">
                                        Аренда</h3>
                                    <p style="font-size: 10.5px; line-height: 1.35; color: rgb(76, 88, 106); margin: 0px 0px 6px;">
                                        Робот на нужный период</p>
                                    <ul style="list-style: none; padding: 0px; margin: 0px; display: grid; gap: 3px;">
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Быстрый
                                            старт
                                        </li>
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Оплата за
                                            срок
                                        </li>
                                    </ul>
                                </article>
                                <article class="fin-scheme-mini">
                                    <div style="position: relative; height: 96px; margin-bottom: 8px;"><img alt="RaaS"
                                                                                                            loading="lazy"
                                                                                                            decoding="async"
                                                                                                            data-nimg="fill"
                                                                                                            style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent; mix-blend-mode: multiply;"
                                                                                                            sizes="180px"
                                                                                                            srcset="~assets/img/raas_009.avif 16w, ~assets/img/raas_014.avif 32w, ~assets/img/raas_002.avif 48w, ~assets/img/raas_016.avif 64w, ~assets/img/raas_015.avif 96w, ~assets/img/raas_004.avif 128w, ~assets/img/raas_003.avif 256w, ~assets/img/raas.avif 384w, ~assets/img/raas_006.avif 640w, ~assets/img/raas_010.avif 750w, ~assets/img/raas_011.avif 828w, ~assets/img/raas_012.avif 1080w, ~assets/img/raas_007.avif 1200w, ~assets/img/raas_013.avif 1920w, ~assets/img/raas_008.avif 2048w, ~assets/img/raas_005.avif 3840w"
                                                                                                            src="~assets/img/raas_005.avif">
                                    </div>
                                    <h3 style="font-size: 13.5px; font-weight: 700; margin: 0px 0px 2px; color: rgb(11, 22, 38);">
                                        RaaS</h3>
                                    <p style="font-size: 10.5px; line-height: 1.35; color: rgb(76, 88, 106); margin: 0px 0px 6px;">
                                        Роботизация как услуга</p>
                                    <ul style="list-style: none; padding: 0px; margin: 0px; display: grid; gap: 3px;">
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Без CAPEX
                                        </li>
                                        <li style="font-size: 10px; color: rgb(11, 22, 38); display: flex; gap: 5px; line-height: 1.3;">
                                            <span aria-hidden="true"
                                                  style="color: rgb(30, 136, 255); font-weight: 800;">✓</span>Сервис
                                            включён
                                        </li>
                                    </ul>
                                </article>
                            </div>
                        </div>
                        <div class="fin-area-request"
                             style="background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1); border-radius: 16px; box-shadow: rgba(31, 73, 136, 0.08) 0px 16px 45px; backdrop-filter: blur(8px); padding: 0px; overflow: hidden; display: grid; grid-template-columns: 1.15fr 0.85fr;">
                            <div style="padding: 18px 8px 18px 18px; display: flex; flex-direction: column; justify-content: center;">
                                <h2 style="font-size: 18px; font-weight: 800; line-height: 1.12; margin: 0px 0px 7px; color: rgb(11, 22, 38); letter-spacing: -0.01em;">
                                    Готовы начать роботизацию?</h2>
                                <p style="font-size: 11px; color: rgb(76, 88, 106); line-height: 1.4; margin: 0px 0px 12px;">
                                    Подготовим варианты финансирования под ваш проект.</p>
                                <NuxtLink to="/robot-selection"
                                        style="align-self: flex-start; height: 40px; padding: 0px 18px; border-radius: 11px; border: medium; background: var(--accent); color: rgb(255, 255, 255); font-weight: 700; font-size: 13px; cursor: pointer; display: inline-flex; align-items: center; gap: 7px;">
                                    Подбор роботов
                                    <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                         fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                         stroke-linejoin="round" class="lucide lucide-arrow-right">
                                        <path d="M5 12h14"></path>
                                        <path d="m12 5 7 7-7 7"></path>
                                    </svg>
                                </NuxtLink>
                            </div>
                            <div style="position: relative; min-width: 0px;"><img alt="Готовы начать роботизацию"
                                                                                  loading="lazy" decoding="async"
                                                                                  data-nimg="fill"
                                                                                  style="position: absolute; height: 100%; width: 100%; inset: 0px; object-fit: contain; color: transparent; mix-blend-mode: multiply;"
                                                                                  sizes="200px"
                                                                                  srcset="~assets/img/ready_010.avif 16w, ~assets/img/ready_008.avif 32w, ~assets/img/ready_014.avif 48w, ~assets/img/ready_004.avif 64w, ~assets/img/ready_002.avif 96w, ~assets/img/ready_011.avif 128w, ~assets/img/ready_009.avif 256w, ~assets/img/ready_012.avif 384w, ~assets/img/ready.avif 640w, ~assets/img/ready_003.avif 750w, ~assets/img/ready_005.avif 828w, ~assets/img/ready_007.avif 1080w, ~assets/img/ready_016.avif 1200w, ~assets/img/ready_006.avif 1920w, ~assets/img/ready_013.avif 2048w, ~assets/img/ready_015.avif 3840w"
                                                                                  src="~assets/img/ready_015.avif">
                            </div>
                        </div>
                    </div>
                    <div class="fin-area-compare"
                         style="background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1); border-radius: 16px; box-shadow: rgba(31, 73, 136, 0.08) 0px 16px 45px; backdrop-filter: blur(8px); padding: 14px; display: flex; flex-direction: column;">
                        <p style="font-size: 13px; font-weight: 700; color: rgb(11, 22, 38); margin: 0px 0px 8px;">
                            Сравнение моделей</p>
                        <div class="fin-cmp-scroll">
                            <table class="fin-cmp-table">
                                <caption class="sr-only">Сравнение моделей финансирования роботизации</caption>
                                <thead>
                                <tr>
                                    <th scope="col"
                                        style="text-align: left; font-size: 10px; font-weight: 600; color: rgb(96, 112, 137); padding: 0px 6px 6px 0px;">
                                        Критерий
                                    </th>
                                    <th scope="col"
                                        style="font-size: 11px; font-weight: 700; color: rgb(20, 32, 51); padding: 0px 4px 6px; white-space: nowrap;">
                                        Покупка
                                    </th>
                                    <th scope="col"
                                        style="font-size: 11px; font-weight: 700; color: rgb(20, 32, 51); padding: 0px 4px 6px; white-space: nowrap;">
                                        Лизинг
                                    </th>
                                    <th scope="col"
                                        style="font-size: 11px; font-weight: 700; color: rgb(20, 32, 51); padding: 0px 4px 6px; white-space: nowrap;">
                                        Аренда
                                    </th>
                                    <th scope="col"
                                        style="font-size: 11px; font-weight: 700; color: rgb(20, 32, 51); padding: 0px 4px 6px; white-space: nowrap;">
                                        RaaS<span
                                            style="display: block; margin-top: 1px; font-size: 8.5px; font-weight: 500; color: rgb(96, 112, 137);">робот как услуга</span>
                                    </th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr style="border-top: 1px solid rgba(36, 83, 151, 0.1);">
                                    <th scope="row"
                                        style="text-align: left; font-size: 11px; font-weight: 500; color: rgb(20, 32, 51); line-height: 1.3; padding: 7px 6px 7px 0px;">
                                        В собственности клиента
                                    </th>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">После выкупа</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Нет"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(217, 74, 74, 0.09); color: rgb(217, 74, 74);">✕</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Нет"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(217, 74, 74, 0.09); color: rgb(217, 74, 74);">✕</span>
                                    </td>
                                </tr>
                                <tr style="border-top: 1px solid rgba(36, 83, 151, 0.1);">
                                    <th scope="row"
                                        style="text-align: left; font-size: 11px; font-weight: 500; color: rgb(20, 32, 51); line-height: 1.3; padding: 7px 6px 7px 0px;">
                                        Низкий стартовый платёж
                                    </th>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Нет"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(217, 74, 74, 0.09); color: rgb(217, 74, 74);">✕</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                </tr>
                                <tr style="border-top: 1px solid rgba(36, 83, 151, 0.1);">
                                    <th scope="row"
                                        style="text-align: left; font-size: 11px; font-weight: 500; color: rgb(20, 32, 51); line-height: 1.3; padding: 7px 6px 7px 0px;">
                                        Подходит для пилота
                                    </th>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Нет"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(217, 74, 74, 0.09); color: rgb(217, 74, 74);">✕</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Частично</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                </tr>
                                <tr style="border-top: 1px solid rgba(36, 83, 151, 0.1);">
                                    <th scope="row"
                                        style="text-align: left; font-size: 11px; font-weight: 500; color: rgb(20, 32, 51); line-height: 1.3; padding: 7px 6px 7px 0px;">
                                        Сервис и поддержка включены
                                    </th>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Отдельно</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Частично</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                </tr>
                                <tr style="border-top: 1px solid rgba(36, 83, 151, 0.1);">
                                    <th scope="row"
                                        style="text-align: left; font-size: 11px; font-weight: 500; color: rgb(20, 32, 51); line-height: 1.3; padding: 7px 6px 7px 0px;">
                                        Оплата за результат
                                    </th>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Нет"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(217, 74, 74, 0.09); color: rgb(217, 74, 74);">✕</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Нет"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(217, 74, 74, 0.09); color: rgb(217, 74, 74);">✕</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Иногда</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span role="img"
                                                                                                              aria-label="Да"
                                                                                                              style="display: inline-grid; place-items: center; width: 18px; height: 18px; border-radius: 50%; font-size: 10.5px; font-weight: 800; line-height: 1; background: rgba(21, 129, 61, 0.1); color: rgb(21, 129, 61);">✓</span>
                                    </td>
                                </tr>
                                <tr style="border-top: 1px solid rgba(36, 83, 151, 0.1);">
                                    <th scope="row"
                                        style="text-align: left; font-size: 11px; font-weight: 500; color: rgb(20, 32, 51); line-height: 1.3; padding: 7px 6px 7px 0px;">
                                        Быстрый старт
                                    </th>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="display: inline-flex; align-items: center; gap: 4px; color: rgb(200, 136, 12); font-size: 10.5px; font-weight: 700;"><span
                                            aria-hidden="true"
                                            style="width: 5px; height: 5px; border-radius: 50%; background: currentcolor; flex-shrink: 0;"></span>Средне</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="display: inline-flex; align-items: center; gap: 4px; color: rgb(200, 136, 12); font-size: 10.5px; font-weight: 700;"><span
                                            aria-hidden="true"
                                            style="width: 5px; height: 5px; border-radius: 50%; background: currentcolor; flex-shrink: 0;"></span>Средне</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="display: inline-flex; align-items: center; gap: 4px; color: rgb(21, 129, 61); font-size: 10.5px; font-weight: 700;"><span
                                            aria-hidden="true"
                                            style="width: 5px; height: 5px; border-radius: 50%; background: currentcolor; flex-shrink: 0;"></span>Быстро</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="display: inline-flex; align-items: center; gap: 4px; color: rgb(21, 129, 61); font-size: 10.5px; font-weight: 700;"><span
                                            aria-hidden="true"
                                            style="width: 5px; height: 5px; border-radius: 50%; background: currentcolor; flex-shrink: 0;"></span>Быстро</span>
                                    </td>
                                </tr>
                                <tr style="border-top: 1px solid rgba(36, 83, 151, 0.1);">
                                    <th scope="row"
                                        style="text-align: left; font-size: 11px; font-weight: 500; color: rgb(20, 32, 51); line-height: 1.3; padding: 7px 6px 7px 0px;">
                                        Риск простоя
                                    </th>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Клиент</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Частично</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Поставщик</span>
                                    </td>
                                    <td style="text-align: center; padding: 7px 4px; line-height: 1.3;"><span
                                            style="font-size: 10.5px; color: rgb(96, 112, 137); font-weight: 500;">Поставщик</span>
                                    </td>
                                </tr>
                                </tbody>
                            </table>
                        </div>
                        <p style="margin: 10px 0px 0px; padding-top: 8px; border-top: 1px solid rgba(36, 83, 151, 0.1); font-size: 10px; line-height: 1.45; color: rgb(76, 88, 106);">
                            Условия зависят от типа проекта, оборудования, срока и финансового профиля компании.</p>
                    </div>
                </div>
            </div>
        </section>
</template>