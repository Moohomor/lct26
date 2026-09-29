<script setup lang="ts">
useHead({ title: 'Пилотирование роботов' })

// Страница показывает, что уже пилотируется: позиции каталога со статусом
// «пилот», с реальными уровнем готовности, отраслью, регионом и ценой.
// Раньше на /pilot-testing страницы не было вовсе — на неё вели ссылки и
// в шапке, и в подвале, и она отдавала 404.
//
// Эффект и окупаемость здесь не показаны: в каталоге их нет, и хранить
// их негде. Считаются они на странице финансирования под конкретный
// объект, поэтому отсюда ведём туда.

const { $fetchApi } = useNuxtApp()

type Item = {
  id: string
  name: string
  status: string
  trl: number | null
  purpose: string | null
  industry: string | null
  region: string | null
  unit_price_rub: number | null
  photo_url: string | null
  vendor?: { name: string; country?: string | null } | null
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
    ? null
    : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(v) + ' ₽'

const all = ref<Item[]>([])
const loadError = ref<string | null>(null)
const industry = ref('')
const search = ref('')

onMounted(async () => {
  try {
    // include_variants=false: комплектации одной техники — это одна тема,
    // и в списке пилотов они занимали бы по несколько строк подряд.
    const list = await $fetchApi<any>('/api/v1/catalog?limit=400&status=piloting&include_variants=false')
    all.value = list?.items ?? []
  } catch (e: any) {
    loadError.value = e?.data?.message ?? 'Не удалось загрузить список пилотов.'
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
      (it.region ?? '').toLowerCase().includes(q)
    )
  })
})

// Распределение по УГТ: у пилота это главный показатель зрелости решения.
const trlBuckets = computed(() => {
  const counts = new Map<number, number>()
  for (const it of all.value) {
    if (it.trl) counts.set(it.trl, (counts.get(it.trl) ?? 0) + 1)
  }
  const max = Math.max(1, ...counts.values())
  return [...counts.entries()]
    .sort((a, b) => a[0] - b[0])
    .map(([trl, count]) => ({ trl, count, height: Math.round((count / max) * 100) }))
})

const stats = computed(() => {
  const list = all.value
  const withTrl = list.filter((it) => it.trl)
  const avgTrl = withTrl.length
    ? (withTrl.reduce((s, it) => s + (it.trl ?? 0), 0) / withTrl.length).toFixed(1)
    : '—'
  return {
    total: list.length,
    avgTrl,
    vendors: new Set(list.map((it) => it.vendor?.name).filter(Boolean)).size,
    types: new Set(list.map((it) => it.solution_type?.code).filter(Boolean)).size,
  }
})
</script>

<template>
    <section class="relative isolate overflow-hidden" style="margin-top: -76px;">
        <div class="pt-wrap">
            <div class="pt-intro">
                <h1>Пилотирование роботов</h1>
                <p>
                    Решения, которые сейчас проходят пилот. Показываем уровень готовности
                    (УГТ), отрасль и регион внедрения — по ним видно, на что ориентироваться
                    при выборе площадки для пилота.
                </p>
            </div>

            <p v-if="loadError" class="pt-note pt-note--bad">{{ loadError }}</p>
            <p v-else-if="!all.length && !loadError" class="pt-note">Загружаем список…</p>

            <template v-else>
                <div class="pt-stats">
                    <div class="pt-stat"><b>{{ stats.total }}</b><span>решений в пилоте</span></div>
                    <div class="pt-stat"><b>{{ stats.avgTrl }}</b><span>средний УГТ</span></div>
                    <div class="pt-stat"><b>{{ stats.vendors }}</b><span>производителей</span></div>
                    <div class="pt-stat"><b>{{ stats.types }}</b><span>типов решений</span></div>
                </div>

                <section v-if="trlBuckets.length" class="pt-card">
                    <h2>Распределение по уровню готовности</h2>
                    <p class="pt-hint">УГТ 9 — технология готова, 6–8 — отлаживается на площадке.</p>
                    <div class="pt-trl">
                        <div v-for="b in trlBuckets" :key="b.trl" class="pt-trl__col">
                            <span class="pt-trl__count">{{ b.count }}</span>
                            <div class="pt-trl__bar">
                                <i :style="{ height: b.height + '%' }"></i>
                            </div>
                            <span class="pt-trl__label">УГТ {{ b.trl }}</span>
                        </div>
                    </div>
                </section>

                <div class="pt-card">
                    <div class="pt-filters">
                        <select v-model="industry" class="pt-input">
                            <option value="">Все отрасли</option>
                            <option v-for="[name, count] in industries" :key="name" :value="name">
                                {{ name }} — {{ count }}
                            </option>
                        </select>
                        <input v-model="search" class="pt-input" type="search"
                               placeholder="Поиск по названию, производителю или региону">
                        <span class="pt-filters__count">Найдено: {{ filtered.length }}</span>
                    </div>

                    <p v-if="!filtered.length" class="pt-note">По этим условиям ничего не нашлось.</p>

                    <ul class="pt-grid">
                        <li v-for="it in filtered" :key="it.id" class="pt-card-item">
                            <NuxtLink :to="`/catalog/${it.id}`" class="pt-item">
                                <div class="pt-item__visual">
                                    <img v-if="photoUrl(it)" :src="photoUrl(it)!" :alt="it.name" loading="lazy">
                                    <span v-else class="pt-item__none">Нет фото</span>
                                </div>
                                <div class="pt-item__body">
                                    <h3>{{ it.name }}</h3>
                                    <p class="pt-item__vendor">{{ it.vendor?.name ?? '—' }}</p>
                                    <div class="pt-item__tags">
                                        <span v-if="it.trl" class="pt-tag pt-tag--trl">УГТ {{ it.trl }}</span>
                                        <span v-if="it.industry" class="pt-tag">{{ it.industry }}</span>
                                        <span v-if="it.region" class="pt-tag">{{ it.region }}</span>
                                    </div>
                                    <p v-if="it.purpose" class="pt-item__purpose">{{ it.purpose }}</p>
                                    <p v-if="it.unit_price_rub" class="pt-item__price">
                                        {{ money(it.unit_price_rub) }}
                                    </p>
                                </div>
                            </NuxtLink>
                        </li>
                    </ul>
                </div>

                <section class="pt-card pt-card--cta">
                    <div>
                        <h2>Посчитайте эффект для своей площадки</h2>
                        <p class="pt-hint">
                            Эффект, окупаемость и стоимость владения считаются под конкретный
                            объект — параметры берутся из справочника, цены — из каталога.
                        </p>
                    </div>
                    <NuxtLink to="/financing" class="pt-btn">Перейти к расчёту</NuxtLink>
                </section>
            </template>
        </div>
    </section>
</template>

<style scoped>
.pt-wrap { max-width: 1440px; margin: 0 auto; padding: 106px clamp(20px, 4vw, 40px) 40px; }
.pt-intro { max-width: 640px; margin-bottom: 18px; }
.pt-intro h1 { margin: 0; font-size: clamp(30px, 3.6vw, 52px); line-height: 1.05;
    letter-spacing: -0.03em; font-weight: 800; color: #0B1626; }
.pt-intro p { margin: 16px 0 0; max-width: 560px; font-size: clamp(14px, 1.4vw, 17px);
    line-height: 1.5; color: #4C586A; }

.pt-card { background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 16px; box-shadow: 0 16px 45px rgba(31, 73, 136, 0.08); backdrop-filter: blur(8px);
    padding: 18px; margin-bottom: 14px; }
.pt-card h2 { margin: 0 0 4px; font-size: 17px; color: #0B1626; }
.pt-hint { margin: 0 0 10px; font-size: 11px; line-height: 1.45; color: #4C586A; }
.pt-note { margin: 0 0 14px; padding: 10px 12px; border-radius: 10px; font-size: 12px; color: #4C586A; }
.pt-note--bad { background: rgba(217, 74, 74, 0.08); color: #B42318; }

.pt-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px;
    margin-bottom: 14px; }
.pt-stat { background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 14px; padding: 14px; }
.pt-stat b { display: block; font-size: 26px; font-weight: 800; color: #0568FF; line-height: 1.1; }
.pt-stat span { font-size: 11px; color: #4C586A; }

.pt-trl { display: flex; align-items: flex-end; gap: 8px; height: 120px; }
/* Столбцы фиксированной ширины: при flex:1 тройка уровней растягивалась
   во всю ширину карточки и читалась не как график, а как три плашки. */
.pt-trl__col { flex: 0 0 76px; display: flex; flex-direction: column; justify-content: flex-end;
    align-items: center; gap: 3px; height: 100%; font-size: 10px; color: #607089; }
.pt-trl__bar { width: 100%; flex: 1; display: flex; align-items: flex-end; background: #F4F8FF;
    border-radius: 6px; overflow: hidden; }
.pt-trl__bar i { display: block; width: 100%; background: #1E88FF; border-radius: 6px 6px 0 0; }
.pt-trl__count { font-weight: 700; color: #0B1626; }
.pt-trl__label { white-space: nowrap; }

.pt-filters { display: flex; gap: 8px; align-items: center; flex-wrap: wrap; margin-bottom: 12px; }
.pt-input { padding: 7px 10px; border: 1px solid #DCE5F2; border-radius: 9px; font-size: 12px;
    color: #0B1626; background: #fff; }
.pt-filters .pt-input[type="search"] { flex: 1; min-width: 200px; }
.pt-filters__count { font-size: 11px; color: #607089; }

.pt-grid { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px;
    grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }
.pt-card-item { display: flex; }
.pt-item { display: flex; flex-direction: column; width: 100%; text-decoration: none; color: inherit;
    background: #FBFDFF; border: 1px solid #EDF1F7; border-radius: 14px; overflow: hidden;
    transition: transform .2s, box-shadow .2s; }
.pt-item:hover { transform: translateY(-2px); box-shadow: 0 10px 24px rgba(38, 69, 118, .12); }
/* flex-shrink:0 и overflow:hidden обязательны: в колоночном флексе блок
   изображения сжимался по контенту, и вытянутое по высоте фото уезжало
   под себя — заголовок наезжал прямо на снимок. */
.pt-item__visual { position: relative; flex: 0 0 128px; height: 128px; background: #fff;
    border-bottom: 1px solid #EDF1F7; display: grid; place-items: center; overflow: hidden; }
.pt-item__visual img { max-height: 100%; max-width: 100%; object-fit: contain; }
.pt-item__none { font-size: 11px; color: #9AA8BD; }
.pt-item__body { padding: 11px 12px 13px; }
.pt-item__body h3 { margin: 0 0 2px; font-size: 13.5px; font-weight: 700; color: #0B1626; }
.pt-item__vendor { margin: 0 0 7px; font-size: 11px; color: #607089; }
.pt-item__tags { display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 7px; }
.pt-tag { font-size: 10px; padding: 2px 7px; border: 1px solid #DCE5F2; border-radius: 999px;
    color: #3C4A63; background: #F7FAFF; }
.pt-tag--trl { border-color: #9BE0B8; color: #067647; background: #ECFDF3; font-weight: 600; }
.pt-item__purpose { margin: 0 0 6px; font-size: 11px; line-height: 1.4; color: #3C4A63; }
.pt-item__price { margin: 0; font-size: 12.5px; font-weight: 700; color: #0568FF; }

.pt-card--cta { display: flex; align-items: center; justify-content: space-between; gap: 16px;
    flex-wrap: wrap; }
.pt-btn { display: inline-flex; align-items: center; height: 40px; padding: 0 18px; border-radius: 11px;
    background: var(--accent, #1E88FF); color: #fff; font-weight: 700; font-size: 13px;
    text-decoration: none; flex-shrink: 0; }

@media (max-width: 600px) {
    .pt-card--cta { flex-direction: column; align-items: flex-start; }
}
</style>
