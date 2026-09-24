<script setup lang="ts">
useHead({
  title: 'Главная',
})
</script>

<template>
  <section class="relative isolate overflow-hidden" style="margin-top:-76px;background:#f4f8ff">
            <div aria-hidden="true" class="absolute inset-0 -z-20 bg-cover bg-no-repeat rm-hero-bg"
                 style="background-position:center top;background-image:url('~/assets/img/hero-wallpaper.jpg')"></div>
            <div aria-hidden="true" class="absolute inset-0 -z-10 rm-hero-veil"
                 style="background:linear-gradient(100deg, rgba(244,248,255,0.94) 0%, rgba(244,248,255,0.72) 38%, rgba(244,248,255,0.18) 60%, rgba(244,248,255,0) 76%)"></div>
            <div aria-hidden="true" class="pointer-events-none absolute inset-x-0 bottom-0 -z-10 h-52"
                 style="background:linear-gradient(180deg, rgba(244,248,255,0) 0%, rgba(244,248,255,0.7) 60%, #f4f8ff 100%)"></div>
            <div class="mx-auto" style="max-width:1440px;padding:140px clamp(20px,4vw,40px) clamp(80px,12vw,150px)">
                <div class="rm-hero-copy" style="width:min(800px, 58%)">
                    <div class="" style="opacity: 1; transform: none;"><p
                            style="display:block;margin:0 0 22px;color:#0067e7;font-size:14px;font-weight:700;text-transform:uppercase;letter-spacing:0.05em">
                        Единое окно роботизации</p></div>
                    <div class="" style="opacity: 1; transform: none;"><h1
                            style="display:block;margin:0;max-width:780px;font-size:clamp(38px,4.4vw,68px);line-height:1.06;letter-spacing:-0.03em;font-weight:800;color:#0b1626">
                        Ваш путь к эффективной роботизации бизнеса</h1></div>
                    <div class="" style="opacity: 1; transform: none;"><p
                            style="display:block;margin:26px 0 0;max-width:640px;font-size:18px;line-height:1.55;color:#4c586a">
                        Подбор, тестирование и финансирование роботов — всё, что нужно для успешного внедрения
                        технологий.</p></div>
                    <div class="" style="opacity: 1; transform: none;">
                        <div class="flex flex-wrap gap-4" style="margin-top:34px"><NuxtLink
                                class="inline-flex items-center gap-3 font-bold text-white transition-transform hover:-translate-y-0.5"
                                style="padding:17px 30px;border-radius:14px;background:var(--accent);font-size:15px;box-shadow:0 14px 32px rgba(30,136,255,0.28)"
                                to="/robot-selection">Начать подбор
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"
                                 stroke-linejoin="round" class="lucide lucide-arrow-right">
                                <path d="M5 12h14"></path>
                                <path d="m12 5 7 7-7 7"></path>
                            </svg>
                        </NuxtLink><NuxtLink class="inline-flex items-center gap-3 font-bold transition-transform hover:-translate-y-0.5"
                               style="padding:17px 28px;border-radius:14px;font-size:15px;color:#0b1626;background:rgba(255,255,255,0.85);border:1px solid rgba(20,55,104,0.12)"
                               to="/catalog">Смотреть каталог
                            <svg xmlns="http://www.w3.org/2000/svg" width="19" height="19" viewBox="0 0 24 24"
                                 fill="none" stroke="var(--accent)" stroke-width="1.8" stroke-linecap="round"
                                 stroke-linejoin="round" class="lucide lucide-layout-grid">
                                <rect width="7" height="7" x="3" y="3" rx="1"></rect>
                                <rect width="7" height="7" x="14" y="3" rx="1"></rect>
                                <rect width="7" height="7" x="14" y="14" rx="1"></rect>
                                <rect width="7" height="7" x="3" y="14" rx="1"></rect>
                            </svg>
                        </NuxtLink></div>
                    </div>
                </div>
            </div>            
        </section>
        <section class="relative z-10" style="background:#f4f8ff;margin-top:-1cm;padding:0 0 56px">
            <div class="mx-auto" style="max-width:1440px;padding:0 clamp(20px,4vw,40px)">
                <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
                    <div class="h-full" style="opacity: 1; transform: none;">
                        <NuxtLink
                            class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                            style="min-height:200px;padding:24px 18px 16px;border-radius:16px;background:rgba(255,255,255,0.94);border:1px solid rgba(36,83,151,0.08);box-shadow:0 16px 45px rgba(31,73,136,0.08)"
                            to="/catalog">
                        <div class="relative z-[2]" style="width:76%"><h2
                                style="display:block;margin:0 0 8px;font-size:16px;line-height:1.2;font-weight:700;color:#0b1626">
                            Каталог роботов</h2>
                            <p style="display:block;margin:0;font-size:11px;line-height:1.5;color:#596476">Тысячи
                                моделей от ведущих производителей</p></div>
                        <img alt="Каталог роботов" loading="lazy" width="320" height="240" decoding="async"
                             data-nimg="1" class="pointer-events-none absolute z-[1] object-contain"
                             style="color:transparent;right:-2px;bottom:-8px;width:60%;height:116px;object-position:right bottom;mix-blend-mode:multiply"
                             srcset="~/assets/img/catalog_002.avif 1x, ~/assets/img/catalog.avif 2x"
                             src="~/assets/img/catalog.avif"><span aria-hidden="true"
                                                                  class="absolute z-[3] grid place-items-center text-white transition-transform group-hover:translate-x-0.5"
                                                                  style="left:18px;bottom:16px;width:28px;height:28px;border-radius:50%;background:var(--accent)"><svg
                            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                            class="lucide lucide-arrow-right"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></NuxtLink>
                    </div>
                    <div class="h-full" style="opacity: 1; transform: none;"><NuxtLink
                            class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                            style="min-height:200px;padding:24px 18px 16px;border-radius:16px;background:rgba(255,255,255,0.94);border:1px solid rgba(36,83,151,0.08);box-shadow:0 16px 45px rgba(31,73,136,0.08)"
                            to="/robot-selection">
                        <div class="relative z-[2]" style="width:76%"><h2
                                style="display:block;margin:0 0 8px;font-size:16px;line-height:1.2;font-weight:700;color:#0b1626">Подбор робота</h2>
                            <p style="display:block;margin:0;font-size:11px;line-height:1.5;color:#596476">
                                Интеллектуальный анализ вашего объекта</p></div>
                        <img alt="AI-аудит" loading="lazy" width="320" height="240" decoding="async" data-nimg="1"
                             class="pointer-events-none absolute z-[1] object-contain"
                             style="color:transparent;right:-2px;bottom:-8px;width:60%;height:116px;object-position:right bottom;mix-blend-mode:multiply"
                             srcset="~/assets/img/ai-audit_002.avif 1x, ~/assets/img/ai-audit.avif 2x"
                             src="~/assets/img/ai-audit.avif"><span aria-hidden="true"
                                                                   class="absolute z-[3] grid place-items-center text-white transition-transform group-hover:translate-x-0.5"
                                                                   style="left:18px;bottom:16px;width:28px;height:28px;border-radius:50%;background:var(--accent)"><svg
                            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                            class="lucide lucide-arrow-right"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></NuxtLink>
                    </div>
                    <div class="h-full" style="opacity: 1; transform: none;"><NuxtLink
                            class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                            style="min-height:200px;padding:24px 18px 16px;border-radius:16px;background:rgba(255,255,255,0.94);border:1px solid rgba(36,83,151,0.08);box-shadow:0 16px 45px rgba(31,73,136,0.08)"
                            to="/pilot-testing">
                        <div class="relative z-[2]" style="width:76%"><h2
                                style="display:block;margin:0 0 8px;font-size:16px;line-height:1.2;font-weight:700;color:#0b1626">
                            Пилотирование</h2>
                            <p style="display:block;margin:0;font-size:11px;line-height:1.5;color:#596476">Быстрый
                                запуск пилота от 2 недель</p></div>
                        <img alt="Пилотирование" loading="lazy" width="320" height="240" decoding="async" data-nimg="1"
                             class="pointer-events-none absolute z-[1] object-contain"
                             style="color:transparent;right:-2px;bottom:-8px;width:60%;height:116px;object-position:right bottom;mix-blend-mode:multiply"
                             srcset="~/assets/img/pilots_002.avif 1x, ~/assets/img/pilots.avif 2x"
                             src="~/assets/img/pilots.avif"><span aria-hidden="true"
                                                                 class="absolute z-[3] grid place-items-center text-white transition-transform group-hover:translate-x-0.5"
                                                                 style="left:18px;bottom:16px;width:28px;height:28px;border-radius:50%;background:var(--accent)"><svg
                            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                            class="lucide lucide-arrow-right"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></NuxtLink>
                    </div>
                    <div class="h-full" style="opacity: 1; transform: none;"><NuxtLink
                            class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                            style="min-height:200px;padding:24px 18px 16px;border-radius:16px;background:rgba(255,255,255,0.94);border:1px solid rgba(36,83,151,0.08);box-shadow:0 16px 45px rgba(31,73,136,0.08)"
                            to="/financing">
                        <div class="relative z-[2]" style="width:76%"><h2
                                style="display:block;margin:0 0 8px;font-size:16px;line-height:1.2;font-weight:700;color:#0b1626">
                            Финансирование</h2>
                            <p style="display:block;margin:0;font-size:11px;line-height:1.5;color:#596476">Лизинг,
                                аренда, RaaS и другие программы</p></div>
                        <img alt="Финансирование" loading="lazy" width="320" height="240" decoding="async" data-nimg="1"
                             class="pointer-events-none absolute z-[1] object-contain"
                             style="color:transparent;right:-2px;bottom:-8px;width:60%;height:116px;object-position:right bottom;mix-blend-mode:multiply"
                             srcset="~/assets/img/finance.avif 1x, ~/assets/img/finance_002.avif 2x"
                             src="~/assets/img/finance_002.avif"><span aria-hidden="true"
                                                                      class="absolute z-[3] grid place-items-center text-white transition-transform group-hover:translate-x-0.5"
                                                                      style="left:18px;bottom:16px;width:28px;height:28px;border-radius:50%;background:var(--accent)"><svg
                            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                            class="lucide lucide-arrow-right"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></NuxtLink>
                    </div>
                    <div class="h-full" style="opacity: 1; transform: none;"><NuxtLink
                            class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                            style="min-height:200px;padding:24px 18px 16px;border-radius:16px;background:rgba(255,255,255,0.94);border:1px solid rgba(36,83,151,0.08);box-shadow:0 16px 45px rgba(31,73,136,0.08)"
                            to="/cases">
                        <div class="relative z-[2]" style="width:76%"><h2
                                style="display:block;margin:0 0 8px;font-size:16px;line-height:1.2;font-weight:700;color:#0b1626">
                            Кейсы</h2>
                            <p style="display:block;margin:0;font-size:11px;line-height:1.5;color:#596476">Реальные
                                проекты и измеримые результаты</p></div>
                        <img alt="Кейсы" loading="lazy" width="320" height="240" decoding="async" data-nimg="1"
                             class="pointer-events-none absolute z-[1] object-contain"
                             style="color:transparent;right:-2px;bottom:-8px;width:60%;height:116px;object-position:right bottom;mix-blend-mode:multiply"
                             srcset="~/assets/img/cases_002.avif 1x, ~/assets/img/cases.avif 2x"
                             src="~/assets/img/cases.avif"><span aria-hidden="true"
                                                                class="absolute z-[3] grid place-items-center text-white transition-transform group-hover:translate-x-0.5"
                                                                style="left:18px;bottom:16px;width:28px;height:28px;border-radius:50%;background:var(--accent)"><svg
                            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                            class="lucide lucide-arrow-right"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></NuxtLink>
                    </div>
                    <div class="h-full" style="opacity: 1; transform: none;"><NuxtLink
                            class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                            style="min-height:200px;padding:24px 18px 16px;border-radius:16px;background:rgba(255,255,255,0.94);border:1px solid rgba(36,83,151,0.08);box-shadow:0 16px 45px rgba(31,73,136,0.08)"
                            to="/contacts">
                        <div class="relative z-[2]" style="width:76%"><h2
                                style="display:block;margin:0 0 8px;font-size:16px;line-height:1.2;font-weight:700;color:#0b1626">
                            Поддержка</h2>
                            <p style="display:block;margin:0;font-size:11px;line-height:1.5;color:#596476">Сопровождение
                                на всех этапах внедрения</p></div>
                        <img alt="Поддержка" loading="lazy" width="320" height="240" decoding="async" data-nimg="1"
                             class="pointer-events-none absolute z-[1] object-contain"
                             style="color:transparent;right:-2px;bottom:-8px;width:60%;height:116px;object-position:right bottom;mix-blend-mode:multiply"
                             srcset="~/assets/img/support.avif 1x, ~/assets/img/support_002.avif 2x"
                             src="~/assets/img/support_002.avif"><span aria-hidden="true"
                                                                      class="absolute z-[3] grid place-items-center text-white transition-transform group-hover:translate-x-0.5"
                                                                      style="left:18px;bottom:16px;width:28px;height:28px;border-radius:50%;background:var(--accent)"><svg
                            xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none"
                            stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"
                            class="lucide lucide-arrow-right"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span></NuxtLink>
                    </div>
                </div>
            </div>
        </section>
</template>

<style scoped>
    @media (max-width: 1024px) {
      .rm-hero-copy { width: 72% !important; }
      .rm-hero-bg { background-position: 64% top !important; }
    }
    @media (max-width: 760px) {
      .rm-hero-copy { width: 100% !important; }
      .rm-hero-bg { background-size: auto 420px !important; background-position: 72% top !important; opacity: 0.9; }
      .rm-hero-veil {
        background: linear-gradient(180deg, rgba(244,248,255,0.5) 0%, rgba(244,248,255,0.82) 28%, rgba(244,248,255,0.96) 44%, #f4f8ff 62%) !important;
      }
    }
</style>
