<script setup lang="ts">
useHead({
  title: 'Подбор робота',
})
</script>

<template>
    <section class="relative overflow-hidden">
            <div class="absolute inset-0 bg-cover bg-center"
                 style="background-image: url(&quot;/ai-audit/bg.jpg&quot;);" aria-hidden="true"></div>
            <div class="absolute inset-0" aria-hidden="true"
                 style="background: linear-gradient(90deg, rgba(255, 255, 255, 0.99) 0%, rgba(255, 255, 255, 0.98) 44%, rgba(250, 253, 255, 0.78) 64%, rgba(244, 249, 255, 0.22) 100%);"></div>
            <div class="absolute inset-0" aria-hidden="true"
                 style="background: radial-gradient(circle at 42% 8%, rgba(203, 225, 255, 0.22), transparent 35%), linear-gradient(rgba(255, 255, 255, 0.06), rgba(247, 250, 255, 0.18));"></div>
            <div class="container relative py-8 lg:py-10">
                <div class="mb-6 max-w-3xl">
                    <h1 class="mt-3.5 text-[clamp(34px,3.35vw,58px)] font-extrabold leading-[1.05] tracking-[-0.035em] text-ink">Подбор робота</h1>
                    <p class="mt-3 text-[16px] leading-[1.65] text-sub">Собираем данные, анализируем ваши процессы<br class="hidden lg:inline"> и выявляем точки роста, автоматизации и экономического эффекта.</p></div>
                <div class="grid gap-[18px] lg:grid-cols-[minmax(0,1.72fr)_minmax(340px,0.92fr)] items-start">
                    <form class="rounded-[17px] border border-[rgba(217,228,242,0.94)] bg-white/[0.86] px-5 py-6 shadow-[0_18px_55px_rgba(37,72,122,0.09)] backdrop-blur-[18px] sm:px-7">
                        <h2 class="mb-5 text-[18px] font-bold tracking-[-0.3px] text-ink">О вашей компании</h2>
                        <div class="grid gap-x-5 gap-y-[17px] sm:grid-cols-[1fr_1.7fr_0.95fr]"><label
                                class="relative block "><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">ИНН компании<span
                                class="text-[color:var(--alert)]"> *</span></span><input inputmode="numeric"
                                                                                         placeholder="10 или 12 цифр"
                                                                                         class="h-[43px] w-full rounded-[7px] border bg-white/80 px-[13px] text-[13px] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"
                                                                                         type="text"></label><label
                                class="relative block sm:col-span-2"><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">Наименование компании<span
                                class="text-[color:var(--alert)]"> *</span></span><input
                                placeholder="Подтянется по ИНН или введите вручную"
                                class="h-[43px] w-full rounded-[7px] border bg-white/80 px-[13px] text-[13px] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"
                                type="text">
                            <div class="mt-1.5 flex flex-wrap gap-1.5"></div>
                        </label><label class="relative block "><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">Город<span
                                class="text-[color:var(--alert)]"> *</span></span>
                            <div class="relative"><select
                                    class="h-[43px] w-full cursor-pointer appearance-none rounded-[7px] border border-[#d7e2f0] bg-white/80 px-3 pr-9 text-[13px] text-ink transition-all focus:border-accent/50 focus:outline-none focus:ring-[3px] focus:ring-accent/10">
                                <option value="Москва" selected="selected">Москва</option>
                                <option value="Санкт-Петербург">Санкт-Петербург</option>
                                <option value="Другой город">Другой город</option>
                            </select>
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                     stroke-linejoin="round"
                                     class="lucide lucide-chevron-down pointer-events-none absolute right-3 top-1/2 h-4 w-4 -translate-y-1/2 text-sub">
                                    <path d="m6 9 6 6 6-6"></path>
                                </svg>
                            </div>
                        </label><label class="relative block "><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">Площадь объектов</span>
                            <div class="relative"><input inputmode="numeric" placeholder="например, 8500"
                                                         class="h-[43px] w-full rounded-[7px] border bg-white/80 px-[13px] text-[13px] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"
                                                         type="text"><span
                                    class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 rounded-md bg-panel px-1.5 py-1 text-[11px] text-faint">м²</span>
                            </div>
                        </label><label class="relative block "><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">Сайт компании</span><input
                                placeholder="https://example.ru"
                                class="h-[43px] w-full rounded-[7px] border bg-white/80 px-[13px] text-[13px] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"
                                type="url"></label></div>
                        <label class="relative block mt-[18px]"><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">Текущие задачи и проблемы<span
                                class="text-[color:var(--alert)]"> *</span></span>
                            <div class="relative"><textarea
                                    placeholder="Опишите ключевые задачи, проблемы, процессы, которые хотите улучшить или автоматизировать. Если знаете — укажите сменность, число людей, примерный ФОТ и объём работ."
                                    rows="4"
                                    class="min-h-[103px] w-full resize-y rounded-[7px] border bg-white/80 px-[15px] pb-7 pt-3 text-[13px] leading-[1.5] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"></textarea><small
                                    class="pointer-events-none absolute bottom-2.5 right-3 text-[10px] text-faint">0 /
                                1200</small></div>
                        </label>
                        <div class="mt-[18px] grid gap-6 sm:grid-cols-[1fr_1.12fr_0.9fr]">
                            <fieldset>
                                <legend class="mb-2.5 text-[11.5px] font-bold text-ink">Тип объекта</legend>
                                <div class="space-y-[9px]"><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Завод / Производство" class="peer sr-only" type="checkbox"
                                        checked="checked"><span aria-hidden="true"
                                                                class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Завод / Производство</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Склад / Логистика" class="peer sr-only" type="checkbox"
                                        checked="checked"><span aria-hidden="true"
                                                                class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Склад / Логистика</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Офис" class="peer sr-only" type="checkbox"><span aria-hidden="true"
                                                                                                     class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Офис</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Торговый центр" class="peer sr-only" type="checkbox"><span
                                        aria-hidden="true"
                                        class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Торговый центр</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Другое" class="peer sr-only" type="checkbox"><span
                                        aria-hidden="true"
                                        class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Другое</span></label></div>
                            </fieldset>
                            <fieldset>
                                <legend class="mb-2.5 text-[11.5px] font-bold text-ink">Процессы для роботизации
                                </legend>
                                <div class="space-y-[9px]"><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Перемещение грузов / внутренняя логистика" class="peer sr-only"
                                        type="checkbox" checked="checked"><span aria-hidden="true"
                                                                                class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Перемещение грузов / внутренняя логистика</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Паллетирование / упаковка" class="peer sr-only"
                                        type="checkbox"><span aria-hidden="true"
                                                              class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Паллетирование / упаковка</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Уборка помещений" class="peer sr-only" type="checkbox"><span
                                        aria-hidden="true"
                                        class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Уборка помещений</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Инвентаризация / инспекция" class="peer sr-only"
                                        type="checkbox"><span aria-hidden="true"
                                                              class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Инвентаризация / инспекция</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Другое" class="peer sr-only" type="checkbox"><span
                                        aria-hidden="true"
                                        class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-[3px] border border-[#9eabbc] bg-white transition-colors peer-checked:border-accent peer-checked:bg-accent peer-checked:[&amp;&gt;svg]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><svg
                                        xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                        fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"
                                        stroke-linejoin="round"
                                        class="lucide lucide-check h-2.5 w-2.5 text-white opacity-0"><path
                                        d="M20 6 9 17l-5-5"></path></svg></span><span>Другое</span></label></div>
                            </fieldset>
                            <fieldset>
                                <legend class="mb-2.5 text-[11.5px] font-bold text-ink">Цель</legend>
                                <div class="space-y-[9px]"><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Купить роботов" class="peer sr-only" type="radio" checked="checked"><span
                                        aria-hidden="true"
                                        class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-full border border-[#a1adbd] bg-white transition-colors peer-checked:border-accent peer-checked:[&amp;&gt;span]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><span
                                        class="h-[7px] w-[7px] rounded-full bg-accent opacity-0 transition-opacity"></span></span><span>Купить роботов</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Аренда / RaaS" class="peer sr-only" type="radio"><span
                                        aria-hidden="true"
                                        class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-full border border-[#a1adbd] bg-white transition-colors peer-checked:border-accent peer-checked:[&amp;&gt;span]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><span
                                        class="h-[7px] w-[7px] rounded-full bg-accent opacity-0 transition-opacity"></span></span><span>Аренда / RaaS</span></label><label
                                        class="flex cursor-pointer select-none items-start gap-2 text-[12px] leading-[1.35] text-ink"><input
                                        aria-label="Пока изучаю варианты" class="peer sr-only" type="radio"><span
                                        aria-hidden="true"
                                        class="mt-px grid h-[15px] w-[15px] shrink-0 place-items-center rounded-full border border-[#a1adbd] bg-white transition-colors peer-checked:border-accent peer-checked:[&amp;&gt;span]:opacity-100 peer-focus-visible:ring-2 peer-focus-visible:ring-accent/40"><span
                                        class="h-[7px] w-[7px] rounded-full bg-accent opacity-0 transition-opacity"></span></span><span>Пока изучаю варианты</span></label>
                                </div>
                            </fieldset>
                        </div>
                        <div class="mt-4 border-t border-line pt-4"></div>
                        <div class="mb-2.5 flex flex-wrap items-baseline justify-between gap-2"><span
                                class="text-[11.5px] font-bold text-ink">Контактные данные <span
                                class="text-[color:var(--alert)]">*</span></span><span class="text-[10.5px] text-faint">Мы свяжемся для уточнения деталей</span>
                        </div>
                        <div class="grid gap-x-5 gap-y-[17px] sm:grid-cols-3"><label class="relative block "><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">Ваше имя<span
                                class="text-[color:var(--alert)]"> *</span></span><input placeholder="Иванов И.И."
                                                                                         class="h-[43px] w-full rounded-[7px] border bg-white/80 px-[13px] text-[13px] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"
                                                                                         type="text"></label><label
                                class="relative block "><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">Телефон<span
                                class="text-[color:var(--alert)]"> *</span></span><input
                                placeholder="+7 (999) 123-45-67"
                                class="h-[43px] w-full rounded-[7px] border bg-white/80 px-[13px] text-[13px] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"
                                type="tel"></label><label class="relative block "><span
                                class="mb-[7px] block text-[11.5px] font-semibold text-ink/80">E-mail<span
                                class="text-[color:var(--alert)]"> *</span></span><input placeholder="ivanov@primer.ru"
                                                                                         class="h-[43px] w-full rounded-[7px] border bg-white/80 px-[13px] text-[13px] text-ink placeholder:text-faint transition-all focus:bg-white focus:outline-none focus:ring-[3px] border-[#d7e2f0] focus:border-accent/50 focus:ring-accent/10"
                                                                                         type="email"></label></div>
                        <div class="mt-4 flex flex-col items-stretch gap-4 sm:flex-row sm:items-center sm:gap-5">
                            <button type="submit"
                                    class="inline-flex h-[43px] min-w-[240px] items-center justify-between gap-3 rounded-[7px] px-5 text-[14px] font-semibold text-accent-ink shadow-[0_10px_24px_rgba(8,101,245,0.20)] transition-all hover:brightness-95 disabled:cursor-not-allowed disabled:opacity-50"
                                    style="background: linear-gradient(135deg, var(--accent), #0059EE);"><span
                                    class="inline-flex items-center gap-2"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                width="24" height="24"
                                                                                viewBox="0 0 24 24" fill="none"
                                                                                stroke="currentColor" stroke-width="2"
                                                                                stroke-linecap="round"
                                                                                stroke-linejoin="round"
                                                                                class="lucide lucide-sparkles h-4 w-4"><path
                                    d="M9.937 15.5A2 2 0 0 0 8.5 14.063l-6.135-1.582a.5.5 0 0 1 0-.962L8.5 9.936A2 2 0 0 0 9.937 8.5l1.582-6.135a.5.5 0 0 1 .963 0L14.063 8.5A2 2 0 0 0 15.5 9.937l6.135 1.581a.5.5 0 0 1 0 .964L15.5 14.063a2 2 0 0 0-1.437 1.437l-1.582 6.135a.5.5 0 0 1-.963 0z"></path><path
                                    d="M20 3v4"></path><path d="M22 5h-4"></path><path d="M4 17v2"></path><path
                                    d="M5 18H3"></path></svg>Подтвердить e-mail и отправить</span>
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                     stroke-linejoin="round" class="lucide lucide-arrow-right h-4 w-4 shrink-0">
                                    <path d="M5 12h14"></path>
                                    <path d="m12 5 7 7-7 7"></path>
                                </svg>
                            </button>
                            <p class="flex items-center gap-2 text-[10px] leading-relaxed text-faint">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                     fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                     stroke-linejoin="round"
                                     class="lucide lucide-shield-check h-[15px] w-[15px] shrink-0">
                                    <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path>
                                    <path d="m9 12 2 2 4-4"></path>
                                </svg>
                                Ваши данные защищены и не передаются третьим лицам
                            </p>
                        </div>
                    </form>
                    <div class="space-y-[18px] scroll-mt-4 lg:sticky lg:top-4">
                        <aside class="rounded-[17px] border border-[rgba(217,228,242,0.94)] bg-gradient-to-b from-white/[0.86] to-[rgba(247,251,255,0.78)] px-7 py-6 shadow-[0_18px_55px_rgba(37,72,122,0.09)] backdrop-blur-[18px]">
                            <h2 class="mb-4 text-[18px] font-bold tracking-[-0.3px] text-ink">Что вы получите</h2>
                            <div class="sm:grid sm:grid-cols-2 sm:gap-x-6 lg:block">
                                <div class="grid grid-cols-[48px_1fr] gap-4 border-b border-line py-3.5 last:border-b-0 sm:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:last-child]:border-b-0">
                                    <span class="grid h-12 w-12 place-items-center rounded-[11px] bg-gradient-to-br from-[#eaf3ff] to-[#f6f9ff] text-accent shadow-[inset_0_0_0_1px_rgba(70,137,240,0.06)]"><svg
                                            xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                                            stroke-linecap="round" stroke-linejoin="round"
                                            class="lucide lucide-chart-column h-[23px] w-[23px]"><path
                                            d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path
                                            d="M13 17V5"></path><path d="M8 17v-3"></path></svg></span>
                                    <div><strong class="block text-[12px] font-semibold leading-[1.45] text-ink">Анализ
                                        процессов и зон для роботизации</strong>
                                        <p class="mt-1 text-[11.5px] leading-[1.65] text-sub">ИИ оценивает текущие
                                            процессы и выявляет узкие места</p></div>
                                </div>
                                <div class="grid grid-cols-[48px_1fr] gap-4 border-b border-line py-3.5 last:border-b-0 sm:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:last-child]:border-b-0">
                                    <span class="grid h-12 w-12 place-items-center rounded-[11px] bg-gradient-to-br from-[#eaf3ff] to-[#f6f9ff] text-accent shadow-[inset_0_0_0_1px_rgba(70,137,240,0.06)]"><svg
                                            xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                                            stroke-linecap="round" stroke-linejoin="round"
                                            class="lucide lucide-trending-up h-[23px] w-[23px]"><polyline
                                            points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline
                                            points="16 7 22 7 22 13"></polyline></svg></span>
                                    <div><strong class="block text-[12px] font-semibold leading-[1.45] text-ink">Расчёт
                                        экономического эффекта</strong>
                                        <p class="mt-1 text-[11.5px] leading-[1.65] text-sub">Показываем потенциальную
                                            экономию и ROI инвестиций</p></div>
                                </div>
                                <div class="grid grid-cols-[48px_1fr] gap-4 border-b border-line py-3.5 last:border-b-0 sm:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:last-child]:border-b-0">
                                    <span class="grid h-12 w-12 place-items-center rounded-[11px] bg-gradient-to-br from-[#eaf3ff] to-[#f6f9ff] text-accent shadow-[inset_0_0_0_1px_rgba(70,137,240,0.06)]"><svg
                                            xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                                            stroke-linecap="round" stroke-linejoin="round"
                                            class="lucide lucide-list-checks h-[23px] w-[23px]"><path
                                            d="m3 17 2 2 4-4"></path><path d="m3 7 2 2 4-4"></path><path
                                            d="M13 6h8"></path><path d="M13 12h8"></path><path
                                            d="M13 18h8"></path></svg></span>
                                    <div><strong class="block text-[12px] font-semibold leading-[1.45] text-ink">Приоритизированный
                                        список решений</strong>
                                        <p class="mt-1 text-[11.5px] leading-[1.65] text-sub">Фокус на тех решениях,
                                            которые дадут максимальный эффект</p></div>
                                </div>
                                <div class="grid grid-cols-[48px_1fr] gap-4 border-b border-line py-3.5 last:border-b-0 sm:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:nth-last-child(-n+2)]:border-b-0 lg:[&amp;:last-child]:border-b-0">
                                    <span class="grid h-12 w-12 place-items-center rounded-[11px] bg-gradient-to-br from-[#eaf3ff] to-[#f6f9ff] text-accent shadow-[inset_0_0_0_1px_rgba(70,137,240,0.06)]"><svg
                                            xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"
                                            stroke-linecap="round" stroke-linejoin="round"
                                            class="lucide lucide-file-text h-[23px] w-[23px]"><path
                                            d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path
                                            d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path
                                            d="M16 13H8"></path><path d="M16 17H8"></path></svg></span>
                                    <div><strong class="block text-[12px] font-semibold leading-[1.45] text-ink">Отчёт с
                                        рекомендациями</strong>
                                        <p class="mt-1 text-[11.5px] leading-[1.65] text-sub">Подробный отчёт с дорожной
                                            картой и оценкой окупаемости — придёт на вашу почту</p></div>
                                </div>
                            </div>
                            <div class="mt-[18px] rounded-[11px] border border-[#bcd6ff] bg-gradient-to-br from-[rgba(239,246,255,0.88)] to-[rgba(224,238,255,0.68)] px-4 py-4">
                                <div class="flex items-center gap-2.5 text-[11.5px] font-bold text-accent">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24"
                                         fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"
                                         stroke-linejoin="round"
                                         class="lucide lucide-shield-check h-[23px] w-[23px] shrink-0">
                                        <path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path>
                                        <path d="m9 12 2 2 4-4"></path>
                                    </svg>
                                    Быстро, безопасно, конфиденциально
                                </div>
                                <div class="mt-3.5 flex flex-wrap justify-between gap-2 text-[9.5px] text-sub"><span
                                        class="inline-flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                    width="24" height="24"
                                                                                    viewBox="0 0 24 24" fill="none"
                                                                                    stroke="currentColor"
                                                                                    stroke-width="2"
                                                                                    stroke-linecap="round"
                                                                                    stroke-linejoin="round"
                                                                                    class="lucide lucide-timer h-3 w-3 text-accent"><line
                                        x1="10" x2="14" y1="2" y2="2"></line><line x1="12" x2="15" y1="14"
                                                                                   y2="11"></line><circle cx="12"
                                                                                                          cy="14"
                                                                                                          r="8"></circle></svg> от 3 дней</span><span
                                        class="inline-flex items-center gap-1"><svg xmlns="http://www.w3.org/2000/svg"
                                                                                    width="24" height="24"
                                                                                    viewBox="0 0 24 24" fill="none"
                                                                                    stroke="currentColor"
                                                                                    stroke-width="2"
                                                                                    stroke-linecap="round"
                                                                                    stroke-linejoin="round"
                                                                                    class="lucide lucide-building2 h-3 w-3 text-accent"><path
                                        d="M6 22V4a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v18Z"></path><path
                                        d="M6 12H4a2 2 0 0 0-2 2v6a2 2 0 0 0 2 2h2"></path><path
                                        d="M18 9h2a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2h-2"></path><path d="M10 6h4"></path><path
                                        d="M10 10h4"></path><path d="M10 14h4"></path><path d="M10 18h4"></path></svg> без выезда</span><span>100% конфиденциально</span>
                                </div>
                            </div>
                        </aside>
                    </div>
                </div>
            </div>
        </section>
</template>