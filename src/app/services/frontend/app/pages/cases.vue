<script setup lang="ts">
useHead({ title: 'Кейсы внедрения роботов' })

// Кейсы собраны из каталога: это решения со статусом «в эксплуатации»,
// сгруппированные по отрасли. Каждая позиция — реальная техника с
// производителем, регионом, ценой и фотографией из каталога внедрения.
//
// Чего на странице нет и почему: цифр эффекта, окупаемости и сроков. В
// каталоге их нет, и хранить негде — каждый расчёт зависит от параметров
// конкретного объекта. Выдумывать «сэкономию 30%» ради красивой карточки
// нельзя, поэтому вместо этого ведём в калькулятор: там та же позиция
// считается на данных объекта.

const { $fetchApi } = useNuxtApp()

type Item = {
  id: string
  name: string
  status: string
  trl: number | null
  purpose: string | null
  description: string | null
  industry: string | null
  region: string | null
  unit_price_rub: number | null
  photo_url: string | null
  vendor?: { name: string } | null
  solution_type?: { code: string; name: string } | null
}

const apiBase = useRuntimeConfig().public.apiBase.replace(/\/$/, '')
const photoUrl = (it: Item) => {
  const url = it.photo_url
  if (!url) return null
  return url.startsWith('http') ? url : `${apiBase}${url}`
}
const money = (v: number | null) =>
  v == null
    ? '—'
    : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(v) + ' ₽'

const all = ref<Item[]>([])
const loadError = ref<string | null>(null)
const industry = ref('')
const search = ref('')

onMounted(async () => {
  try {
    const list = await $fetchApi<any>(
      '/api/v1/catalog?limit=400&status=operation&include_variants=false',
    )
    all.value = list?.items ?? []
  } catch (e: any) {
    loadError.value = e?.data?.message ?? 'Не удалось загрузить кейсы.'
  }
})

const industries = computed(() => {
  const counts = new Map<string, number>()
  for (const it of all.value) {
    if (it.industry) counts.set(it.industry, (counts.get(it.industry) ?? 0) + 1)
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1])
})

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  return all.value.filter((it) => {
    if (industry.value && it.industry !== industry.value) return false
    if (!q) return true
    return (
      (it.name ?? '').toLowerCase().includes(q) ||
      (it.vendor?.name ?? '').toLowerCase().includes(q) ||
      (it.region ?? '').toLowerCase().includes(q) ||
      (it.purpose ?? '').toLowerCase().includes(q)
    )
  })
})

const regions = computed(() => new Set(all.value.map((i) => i.region).filter(Boolean)).size)
const withPhoto = computed(() => all.value.filter((i) => i.photo_url).length)
</script>

<template>
    <section class="relative isolate overflow-hidden" style="margin-top: -76px;">
        <div class="bc-wrap">
            <div class="bc-intro">
                <h1>Кейсы внедрения</h1>
                <p>
                    Роботизация, работающая у заказчиков: техника, отрасли и регионы, где она
                    уже эксплуатируется. Откройте карточку позиции или посчитайте эффект
                    для своего объекта.
                </p>
            </div>

            <p v-if="loadError" class="bc-note bc-note--bad">{{ loadError }}</p>
            <p v-else-if="!all.length && !loadError" class="bc-note">Загружаем кейсы…</p>

            <template v-else>
                <div class="bc-stats">
                    <div class="bc-stat"><b>{{ all.length }}</b><span>внедрений</span></div>
                    <div class="bc-stat"><b>{{ industries.length }}</b><span>отраслей</span></div>
                    <div class="bc-stat"><b>{{ regions }}</b><span>регионов</span></div>
                    <div class="bc-stat"><b>{{ withPhoto }}</b><span>с фотографией</span></div>
                </div>

                <div class="bc-card">
                    <div class="bc-filters">
                        <select v-model="industry" class="bc-input">
                            <option value="">Все отрасли</option>
                            <option v-for="[name, count] in industries" :key="name" :value="name">
                                {{ name }} — {{ count }}
                            </option>
                        </select>
                        <input v-model="search" class="bc-input" type="search"
                               placeholder="Поиск по технике, производителю, региону или задаче">
                        <span class="bc-filters__count">Найдено: {{ filtered.length }}</span>
                    </div>

                    <p class="bc-source">
                        Источник: каталог внедрения ФЦ БАС, позиции со статусом «в эксплуатации».
                        Оценка экономии, окупаемости и сроков зависит от параметров объекта
                        и считается в калькуляторе — в каталоге этих цифр нет.
                    </p>

                    <p v-if="!filtered.length" class="bc-note">По этим условиям ничего не нашлось.</p>

                    <ul class="bc-grid">
                        <li v-for="it in filtered" :key="it.id" class="bc-item">
                            <NuxtLink :to="`/catalog/${it.id}`" class="bc-item__link">
                                <div class="bc-item__visual">
                                    <img v-if="photoUrl(it)" :src="photoUrl(it)!" :alt="it.name" loading="lazy">
                                    <span v-else class="bc-item__none">Нет фото</span>
                                </div>
                                <div class="bc-item__body">
                                    <h3>{{ it.name }}</h3>
                                    <p class="bc-item__vendor">{{ it.vendor?.name ?? '—' }}</p>
                                    <div class="bc-item__tags">
                                        <span class="bc-tag bc-tag--ok">В эксплуатации</span>
                                        <span v-if="it.industry" class="bc-tag">{{ it.industry }}</span>
                                        <span v-if="it.region" class="bc-tag">{{ it.region }}</span>
                                        <span v-if="it.trl" class="bc-tag">УГТ {{ it.trl }}</span>
                                    </div>
                                    <p v-if="it.description || it.purpose" class="bc-item__text">
                                        {{ it.description || it.purpose }}
                                    </p>
                                    <p class="bc-item__price">{{ money(it.unit_price_rub) }}</p>
                                </div>
                            </NuxtLink>
                        </li>
                    </ul>
                </div>

                <section class="bc-card bc-card--cta">
                    <div>
                        <h2>Посчитайте экономику для своего объекта</h2>
                        <p class="bc-hint">
                            Стоимость владения, окупаемость и чувствительность к допущениям —
                            на параметрах вашего склада, производства или аэропорта.
                        </p>
                    </div>
                    <div class="bc-cta__links">
                        <NuxtLink to="/financing" class="bc-btn">Рассчитать</NuxtLink>
                        <NuxtLink to="/catalog" class="bc-btn bc-btn--ghost">Весь каталог</NuxtLink>
                    </div>
                </section>
            </template>
        </div>
    </section>
</template>

<style scoped>
.bc-wrap { max-width: 1440px; margin: 0 auto; padding: 106px clamp(20px, 4vw, 40px) 40px; }
.bc-intro { max-width: 640px; margin-bottom: 18px; }
.bc-intro h1 { margin: 0; font-size: clamp(30px, 3.6vw, 52px); line-height: 1.05;
    letter-spacing: -0.03em; font-weight: 800; color: #0B1626; }
.bc-intro p { margin: 16px 0 0; max-width: 560px; font-size: clamp(14px, 1.4vw, 17px);
    line-height: 1.5; color: #4C586A; }

.bc-card { background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 16px; box-shadow: 0 16px 45px rgba(31, 73, 136, 0.08); backdrop-filter: blur(8px);
    padding: 18px; margin-bottom: 14px; }
.bc-card h2 { margin: 0 0 4px; font-size: 17px; color: #0B1626; }
.bc-hint { margin: 0; font-size: 11px; line-height: 1.45; color: #4C586A; }
.bc-note { margin: 0 0 14px; padding: 10px 12px; border-radius: 10px; font-size: 12px; color: #4C586A; }
.bc-note--bad { background: rgba(217, 74, 74, 0.08); color: #B42318; }
.bc-source { margin: 0 0 14px; padding: 9px 11px; border-radius: 10px; background: #F4F8FF;
    font-size: 10.5px; line-height: 1.5; color: #4C586A; }

.bc-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;
    margin-bottom: 14px; }
.bc-stat { background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 14px; padding: 14px; }
.bc-stat b { display: block; font-size: 26px; font-weight: 800; color: #0568FF; line-height: 1.1; }
.bc-stat span { font-size: 11px; color: #4C586A; }

.bc-filters { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 10px; }
.bc-input { padding: 7px 10px; border: 1px solid #DCE5F2; border-radius: 9px; font-size: 12px;
    color: #0B1626; background: #fff; }
.bc-filters .bc-input[type="search"] { flex: 1; min-width: 200px; }
.bc-filters__count { font-size: 11px; color: #607089; }

.bc-grid { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); }
.bc-item { display: flex; }
.bc-item__link { display: flex; flex-direction: column; width: 100%; text-decoration: none;
    color: inherit; background: #FBFDFF; border: 1px solid #EDF1F7; border-radius: 14px;
    overflow: hidden; transition: transform .2s, box-shadow .2s; }
.bc-item__link:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(38, 69, 118, .12); }
/* flex-shrink:0 и overflow:hidden обязательны: в колоночном флексе блок
   изображения сжимался по контенту, и вытянутое по высоте фото уезжало
   под себя — название наезжало прямо на снимок. */
.bc-item__visual { flex: 0 0 140px; height: 140px; background: #fff;
    border-bottom: 1px solid #EDF1F7; display: grid; place-items: center; overflow: hidden; }
.bc-item__visual img { max-height: 100%; max-width: 100%; object-fit: contain; }
.bc-item__none { font-size: 11px; color: #9AA8BD; }
.bc-item__body { padding: 11px 12px 13px; }
.bc-item__body h3 { margin: 0 0 2px; font-size: 13.5px; font-weight: 700; color: #0B1626; }
.bc-item__vendor { margin: 0 0 7px; font-size: 11px; color: #607089; }
.bc-item__tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 7px; }
.bc-tag { font-size: 10px; padding: 2px 7px; border: 1px solid #DCE5F2; border-radius: 999px;
    color: #3C4A63; background: #F7FAFF; }
.bc-tag--ok { border-color: #9BE0B8; color: #067647; background: #ECFDF3; font-weight: 600; }
.bc-item__text { margin: 0 0 6px; font-size: 11px; line-height: 1.4; color: #3C4A63;
    display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 3; overflow: hidden; }
.bc-item__price { margin: 0; font-size: 12.5px; font-weight: 700; color: #0568FF; }

.bc-card--cta { display: flex; align-items: center; justify-content: space-between; gap: 16px;
    flex-wrap: wrap; }
.bc-cta__links { display: flex; gap: 8px; flex-shrink: 0; }
.bc-btn { display: inline-flex; align-items: center; height: 40px; padding: 0 18px; border-radius: 11px;
    background: var(--accent, #1E88FF); color: #fff; font-weight: 700; font-size: 13px;
    text-decoration: none; }
.bc-btn--ghost { background: transparent; color: #0568FF; border: 1px solid #1E88FF; }

@media (max-width: 600px) {
    .bc-card--cta { flex-direction: column; align-items: flex-start; }
}
</style>
