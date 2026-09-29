<script setup lang="ts">
useHead({
  title: 'Главная',
})

// Главная собирает цифры из каталога, а не из макета. Раньше здесь стояли
// «тысячи моделей» при 226 позициях, «измеримые результаты» у кейсов, у
// которых таких результатов нет, и обещание пилота «от 2 недель», которого
// нигде не зафиксировано. Для показа это опасно: первая же проверка по
// каталогу опровергает текст.
const { $fetchApi } = useNuxtApp()

const stats = ref<any>(null)
const loadError = ref<string | null>(null)

onMounted(async () => {
  try {
    stats.value = await $fetchApi('/api/v1/catalog/stats')
  } catch (e: any) {
    loadError.value = e?.data?.message ?? 'Каталог временно недоступен.'
  }
})

const statusCount = (code: string) =>
  stats.value?.by_status?.find((s: any) => s.status === code)?.count ?? 0

// Разделы главной описывают то, что платформа действительно делает.
// «Лизинг, аренда» и «измеримые результаты» убраны: таких моделей и цифр
// в платформе нет, а обещание, которое не выполняется, хуже отсутствия.
// Тексты короткие: карточка узкая — в шести колонках длинное описание
// наезжает на иллюстрацию.
const SECTIONS = [
  {
    to: '/catalog',
    title: 'Каталог роботов',
    text: 'Цены, фото и характеристики',
    img: 'catalog',
  },
  {
    to: '/robot-selection',
    title: 'Подбор робота',
    text: 'Пригодность под ваш объект',
    img: 'ai-audit',
  },
  {
    to: '/pilot-testing',
    title: 'Пилотирование',
    text: 'Что пилотируется сейчас',
    img: 'pilots',
  },
  {
    to: '/financing',
    title: 'Финансирование',
    text: 'Окупаемость и стоимость владения',
    img: 'finance',
  },
  {
    to: '/cases',
    title: 'Кейсы',
    text: 'Техника, что уже работает',
    img: 'cases',
  },
  {
    to: '/contacts',
    title: 'Доступ и поддержка',
    text: 'Демо-учётные записи',
    img: 'support',
  },
]

import catalogImg from '~/assets/img/catalog.avif'
import aiAuditImg from '~/assets/img/ai-audit.avif'
import pilotsImg from '~/assets/img/pilots.avif'
import financeImg from '~/assets/img/finance.avif'
import casesImg from '~/assets/img/cases.avif'
import supportImg from '~/assets/img/support.avif'
import heroImg from '~/assets/img/ad377695-0589-4c54-82ae-a13a5920b8ff.png'

const sectionImage = (name: string) =>
  ({
    catalog: catalogImg,
    'ai-audit': aiAuditImg,
    pilots: pilotsImg,
    finance: financeImg,
    cases: casesImg,
    support: supportImg,
  })[name] ?? ''
</script>

<template>
  <section class="relative isolate overflow-hidden" style="margin-top:-76px;"
           :style="{ '--hero': `url(${heroImg})` }">
            <div class="mx-auto bg-rorbot" style="max-width:1440px;padding:140px clamp(20px,4vw,40px) clamp(80px,12vw,150px)">
                <div class="rm-hero-copy relative" style="width:min(800px, 58%)">
                    <div class="" style="opacity: 1; transform: none;"><h1
                            style="display:block;margin:0;max-width:780px;font-size:3.3rem;line-height:1.06;letter-spacing:-0.03em;font-weight:800;color:#0b1626">
                        Подбор <span style="color: #348bdc;">роботизированных решений</span> с расчётом экономики и визуализацией</h1></div>
                    <div class="" style="opacity: 1; transform: none;"><p
                            style="display:block;margin:26px 0 0;max-width:640px;font-size:18px;line-height:1.55;color:rgb(7, 41, 94)">
                        Платформа помогает за несколько минут пройти путь от параметров объекта до обоснованной гипотезы о роботизации: каталог решений, подбор, сравнение сценариев, экономический эффект, окупаемость и 2D-имитация работы роботов.</p></div>
                    
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
        <section v-if="stats" class="rm-stats" aria-label="Каталог в цифрах">
            <div class="rm-stats__inner">
                <div class="rm-stats__cell">
                    <b>{{ stats.total }}</b><span>решений в каталоге</span>
                </div>
                <div class="rm-stats__cell">
                    <b>{{ stats.vendors }}</b><span>производителей</span>
                </div>
                <div class="rm-stats__cell">
                    <b>{{ statusCount('operation') }}</b><span>в эксплуатации</span>
                </div>
                <div class="rm-stats__cell">
                    <b>{{ statusCount('piloting') }}</b><span>в пилоте</span>
                </div>
                <div class="rm-stats__cell">
                    <b>{{ statusCount('rnd') }}</b><span>в НИОКР</span>
                </div>
                <div class="rm-stats__cell">
                    <b>{{ stats.price_coverage_pct }}%</b><span>позиций с ценой</span>
                </div>
            </div>
        </section>
        <p v-if="loadError" class="rm-stats__error">{{ loadError }}</p>

        <section class="relative z-10 rm-sections">
            <div class="mx-auto" style="max-width:1440px;padding:0 clamp(20px,4vw,40px)">
                <div class="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6">
                    <div v-for="(s, i) in SECTIONS" :key="s.to" class="h-full rm-section">
                        <NuxtLink
                                class="rm-service-card group relative block h-full overflow-hidden transition-transform hover:-translate-y-1"
                                :class="i % 3 === 0 ? 'rm-service-card--left' : 'rm-service-card--right'"
                                :style="{ minHeight: '200px', padding: '24px 18px 16px' }"
                                :to="s.to">
                        <div class="rm-service-card__text">
                            <h2 style="display:block;margin:0 0 8px;font-size:15px;line-height:1.2;font-weight:700;color:#0b1626">
                                {{ s.title }}
                            </h2>
                            <p style="display:block;margin:0;font-size:11px;line-height:1.45;color:#596476">
                                {{ s.text }}
                            </p>
                        </div>
                        <img :alt="s.title" loading="lazy" decoding="async"
                             class="rm-service-card__img pointer-events-none absolute z-[1] object-contain"
                             :style="{
                                 [i % 3 === 0 ? 'right' : 'left']: '-2px',
                                 bottom: '-8px',
                                 width: '104px',
                                 height: '104px',
                             }"
                             :src="sectionImage(s.img)">
                        </NuxtLink>
                    </div>
                </div>
            </div>
        </section>
</template>

<style scoped>
.bg-rorbot {
    position: relative;
}

/* Путь к иллюстрации приходит переменной: в CSS обращение
   url('~/assets/...') не собирается, картинка просто не находится. */
.bg-rorbot::before {
    content: "";
    background-image: var(--hero);
    background-position: right bottom;
    background-repeat: no-repeat;
    background-size: contain;
    position: absolute;
    height: 100%;
    bottom: 0;
    left: 0;
    right: 0;
    transform: translate(83px, 0);
    opacity: .75;
}

.rm-stats {
    position: relative;
    z-index: 10;
    max-width: 1440px;
    margin: -34px auto 0;
    padding: 0 clamp(20px, 4vw, 40px);
}

.rm-stats__inner {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
}

.rm-stats__cell {
    padding: 13px 14px;
    border-radius: 14px;
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(36, 83, 151, 0.08);
    box-shadow: 0 12px 30px rgba(31, 73, 136, 0.08);
}

.rm-stats__cell b {
    display: block;
    font-size: 24px;
    font-weight: 800;
    color: #0568ff;
    line-height: 1.1;
}

.rm-stats__cell span {
    font-size: 11px;
    color: #596476;
}

.rm-stats__error {
    position: relative;
    z-index: 10;
    max-width: 1440px;
    margin: 8px auto 0;
    padding: 0 clamp(20px, 4vw, 40px);
    font-size: 11px;
    color: #b42318;
}

.rm-sections {
    margin-top: -1cm;
    padding-bottom: 56px;
}

.rm-section {
    opacity: 1;
    transform: none;
}

/* Чередование формы карточек повторяет исходную вёрстку: скругления
   чередуются через колонку, часть карточек — с зелёным градиентом. */
.rm-service-card {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(36, 83, 151, 0.08);
    box-shadow: 0 16px 45px rgba(31, 73, 136, 0.08);
}

.rm-service-card--left {
    border-radius: 0 100px 10px 100px;
    background: linear-gradient(-220deg, rgb(226, 237, 188) 0%, rgb(229, 255, 177) 38%,
            rgb(192, 219, 96) 80%, rgb(148, 208, 78) 100%);
}

.rm-service-card--right {
    border-radius: 100px 0 100px 10px;
    display: flex;
    justify-content: flex-end;
    text-align: right;
    background: linear-gradient(220deg, rgb(226, 237, 188) 0%, rgb(229, 255, 177) 38%,
            rgb(192, 219, 96) 80%, rgb(148, 208, 78) 100%);
}

.rm-section:nth-child(3n + 1) .rm-service-card {
    background: rgba(255, 255, 255, 0.94);
}

/* Текст не заходит на иллюстрацию: в шести колонках карточка узкая, а
   рисунок высотой 104px занимает нижний угол. Нижний отступ держит
   описание выше зоны картинки, ширина не даёт наехать сбоку. */
.rm-service-card__text {
    position: relative;
    z-index: 2;
    width: 74%;
    padding-bottom: 96px;
}

.rm-service-card__text h2 {
    overflow-wrap: anywhere;
}

.rm-service-card__text p {
    display: -webkit-box;
    -webkit-box-orient: vertical;
    -webkit-line-clamp: 3;
    overflow: hidden;
}

.rm-service-card__img {
    color: transparent;
    object-position: right bottom;
    mix-blend-mode: multiply;
}

@media (max-width: 1024px) {
    .rm-hero-copy {
        width: 72% !important;
    }

    .rm-hero-bg {
        background-position: 64% top !important;
    }
}

@media (max-width: 760px) {
    .rm-hero-copy {
        width: 100% !important;
    }

    .rm-hero-bg {
        background-size: auto 420px !important;
        background-position: 72% top !important;
        opacity: 0.9;
    }

    .bg-rorbot::before {
        transform: translate(0, 0);
        opacity: .5;
    }
}
</style>
