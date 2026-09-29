<script setup lang="ts">
useHead({
  title: 'Каталог роботов',
})

// Каталог читается из API: позиции, статистика и значения для фильтров
// приходят из базы. Раньше здесь был статичный макет из шести роботов Pudu
// с выдуманными числами — он ничего не говорил о том, что есть на самом деле.
const { $fetchApi } = useNuxtApp()

type Vendor = { id: number; name: string; country?: string | null }
type SolutionType = { id: number; code: string; name: string }
type Solution = {
  id: string
  name: string
  vendor: Vendor | null
  solution_type: SolutionType | null
  status: string
  trl: number | null
  purpose: string | null
  description: string | null
  industry: string | null
  region: string | null
  unit_price_rub: number | null
  price_source: string | null
  completeness: number
  is_verified: boolean
}

const PAGE_SIZE = 60

const search = ref('')
const typeCode = ref('')
const industry = ref('')
const status = ref('')
const minTrl = ref('')
const page = ref(1)

const query = computed(() => {
  const q: Record<string, string> = {}
  if (search.value.trim()) q.search = search.value.trim()
  if (typeCode.value) q.solution_type = typeCode.value
  if (industry.value) q.industry = industry.value
  if (status.value) q.status = status.value
  if (minTrl.value) q.min_trl = minTrl.value
  q.limit = String(PAGE_SIZE)
  q.offset = String((page.value - 1) * PAGE_SIZE)
  return q
})

const { data: listing, pending } = await useAsyncData(
  'catalog',
  () => $fetchApi('/api/v1/catalog', { query: query.value }),
  { watch: [query] },
)

const { data: stats } = await useAsyncData('catalog-stats', () =>
  $fetchApi('/api/v1/catalog/stats'),
)

const { data: facets } = await useAsyncData('catalog-facets', () =>
  $fetchApi('/api/v1/catalog/facets'),
)

const items = computed<Solution[]>(() => (listing.value?.items as Solution[]) ?? [])

// Список по умолчанию скрывает комплектации (include_variants=false), поэтому
// в шапке показываем то же число, что и в выдаче: 226 строк в базе, но
// 190 моделей. Показывать 226 означало бы обещать больше, чем откроется.
const catalogSize = computed(() => {
  const s = stats.value as { total?: number; variants?: number } | null
  if (!s) return 0
  return (s.total ?? 0) - (s.variants ?? 0)
})

const total = computed(() => listing.value?.total ?? 0)
const pages = computed(() => Math.max(1, Math.ceil(total.value / PAGE_SIZE)))

const STATUS_LABEL: Record<string, string> = {
  operation: 'В эксплуатации',
  piloting: 'Пилот',
  rnd: 'НИОКР',
}

// Любой фильтр сбрасывает страницу на первую: иначе после сужения выборки
// пользователь оказывается на пустой странице 3 из 1.
watch([search, typeCode, industry, status, minTrl], () => {
  page.value = 1
})

const hasFilters = computed(
  () =>
    Boolean(search.value || typeCode.value || industry.value || status.value || minTrl.value),
)

function resetFilters() {
  search.value = ''
  typeCode.value = ''
  industry.value = ''
  status.value = ''
  minTrl.value = ''
  page.value = 1
}

function price(s: Solution): string {
  if (s.unit_price_rub === null || s.unit_price_rub === undefined) return 'Цена по запросу'
  return new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(s.unit_price_rub) + ' ₽'
}

function maker(s: Solution): string {
  const name = s.vendor?.name ?? 'Производитель не указан'
  const country = s.vendor?.country
  return country ? `${name} · ${country}` : name
}

// Картинок у решений в базе нет, поэтому визуальный блок — инициалы типа.
// Подставлять выдуманные фото значило бы выдавать чужую продукцию за
// организаторскую.
function initials(s: Solution): string {
  const source = s.solution_type?.name ?? s.name
  return source
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0] ?? '')
    .join('')
    .toUpperCase()
}

function vendorCount(s: Solution): string {
  return s.is_verified ? 'ТТХ подтверждены организатором' : 'ТТХ из каталога решений'
}
</script>

<template>
    <div>
            <div class="rmc-root">
                <div class="rmc-shell">
                    <section class="rmc-hero">
                        <div><h1 class="rmc-h1">Каталог роботов</h1>
                            <p class="rmc-lead">Подберите идеальную автоматизацию для вашего бизнеса. Анализируйте технические параметры, стоимость и условия от надежных поставщиков в одном месте.</p></div>
                        <div class="rmc-stats">
                            <article class="rmc-stat"><span class="rmc-stat-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-boxes"><path
                                    d="M2.97 12.92A2 2 0 0 0 2 14.63v3.24a2 2 0 0 0 .97 1.71l3 1.8a2 2 0 0 0 2.06 0l3-1.8a2 2 0 0 0 .97-1.71v-3.24a2 2 0 0 0-.97-1.71l-3-1.8a2 2 0 0 0-2.06 0l-3 1.8a2 2 0 0 0-.97 1.71z"></path><path
                                    d="m7 16.5-4.74-2.85"></path><path d="m7 16.5 4.74-2.85"></path><path
                                    d="M7 16.5v5.17"></path><path
                                    d="M12 13.5V19l5.03 2.38a2 2 0 0 0 2.06 0L22 19v-3.24a2 2 0 0 0-.97-1.71l-5-1.8a2 2 0 0 0-2.06 0l-5 1.8a2 2 0 0 0-.97 1.71z"></path><path
                                    d="m17 16.5-4.74-2.85"></path><path d="m17 16.5 4.74-2.85"></path><path
                                    d="M17 16.5v5.17"></path><path
                                    d="M7.97 4.42a2 2 0 0 0-1.47 0L2.97 6.21a2 2 0 0 0-.97 1.71v3.24a2 2 0 0 0 .97 1.71l3.5 1.8a2 2 0 0 0 1.47 0l3.53-1.8a2 2 0 0 0 .97-1.71V7.92a2 2 0 0 0-.97-1.71z"></path><path
                                    d="M12 8 7.26 5.15"></path><path d="M12 8v3.24"></path><path
                                    d="M12 8l4.74-2.85"></path><path d="M12 8v3.24"></path></svg></span><span><b>{{
                                    catalogSize }}</b><span
                                    class="rmc-stat-label">моделей роботов</span></span>
                            </article>
                            <article class="rmc-stat"><span class="rmc-stat-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-factory"><path
                                    d="M2 20a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2V8l-7 5V8l-7 5V4a2 2 0 0 0-2-2H4a2 2 0 0 0-2 2z"></path><path
                                    d="M17 18h1"></path><path d="M12 18h1"></path><path d="M7 18h1"></path></svg></span><span><b>{{
                                    stats?.vendors ?? 0 }}</b><span
                                    class="rmc-stat-label">производителей</span></span></article>                            <article class="rmc-stat"><span class="rmc-stat-icon"><svg
                                    xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                                    fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                    stroke-linejoin="round" class="lucide lucide-users"><path
                                    d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle
                                    cx="9" cy="7" r="4"></circle><path
                                    d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path
                                    d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg></span><span><b>{{
                                    stats?.by_status?.find((s: any) => s.status === 'operation')?.count ?? 0 }}</b><span
                                    class="rmc-stat-label">внедрено в производстве</span></span>
                            </article>
                        </div>
                    </section>

                    <div style="margin-top:1rem; margin-bottom: 1rem;;">
                        <label class="rmc-search"><svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-search"><circle cx="11" cy="11" r="8"></circle><path d="m21 21-4.3-4.3"></path></svg><input
                            v-model="search" placeholder="Поиск по названию, назначению, описанию..." aria-label="Поиск роботов" type="search">
                    </label>
                    </div>

                    <div class="rmc-filter-panel flex gap-3">
                        <div class="rmc-filter-panel__sidebar_left">
                            <section class="rmc-panel">
                        <div class="rmc-filters">
                            <label class="rmc-field"><span>Категория</span><select v-model="typeCode">
                                <option value="">Все категории</option>
                                <option v-for="t in facets?.solution_types ?? []" :key="t.value" :value="t.value">
                                    {{ t.label }} ({{ t.count }})
                                </option>
                            </select></label>
                            <label class="rmc-field"><span>Отрасль</span><select v-model="industry">
                                <option value="">Все отрасли</option>
                                <option v-for="i in facets?.industries ?? []" :key="i.value" :value="i.value">
                                    {{ i.value }} ({{ i.count }})
                                </option>
                            </select></label>
                            <label class="rmc-field"><span>Статус</span><select v-model="status">
                                <option value="">Все статусы</option>
                                <option v-for="s in facets?.statuses ?? []" :key="s.value" :value="s.value">
                                    {{ STATUS_LABEL[s.value] ?? s.value }} ({{ s.count }})
                                </option>
                            </select></label>
                            <label class="rmc-field"><span>Готовность (УГТ)</span><select v-model="minTrl">
                                <option value="">Любая</option>
                                <option value="9">9 — серийное производство</option>
                                <option value="8">8 и выше</option>
                                <option value="7">7 и выше</option>
                                <option value="6">6 и выше</option>
                                <option value="5">5 и выше</option>
                            </select></label>
                        </div>
                        <button v-if="hasFilters" type="button" class="rmc-reset" @click="resetFilters">
                            Сбросить фильтры
                        </button>
                        </section>
                        </div>
                    </div>

                    <section class="rmc-grid" v-if="items.length">
                        <article v-for="s in items" :key="s.id" class="rmc-card">
                            <span class="rmc-badge" v-if="s.status !== 'operation'">{{
                                STATUS_LABEL[s.status] ?? s.status
                            }}</span>
                            <div class="rmc-visual rmc-visual--initials"><span>{{ initials(s) }}</span></div>
                            <div class="rmc-body">
                                <h3><a class="rmc-stretch" href="#">{{ s.name }}</a></h3>
                                <p class="rmc-maker">{{ maker(s) }}</p>
                                <p class="rmc-desc">{{ s.purpose || s.description || 'Назначение не указано' }}</p>
                                <div class="rmc-tags">
                                    <span v-if="s.solution_type">{{ s.solution_type.name }}</span>
                                    <span v-if="s.industry">{{ s.industry }}</span>
                                    <span v-if="s.trl">УГТ {{ s.trl }}</span>
                                </div>
                                <div class="rmc-foot">
                                    <div>
                                        <div class="rmc-price">{{ price(s) }}</div>
                                        <div class="rmc-sup">{{ vendorCount(s) }}</div>
                                    </div>
                                    <span class="rmc-go" aria-hidden="true"><svg
                                            xmlns="http://www.w3.org/2000/svg" width="14" height="14"
                                            viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                                            stroke-linecap="round" stroke-linejoin="round"
                                            class="lucide lucide-arrow-right"><path
                                            d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg></span>
                                </div>
                            </div>
                        </article>
                    </section>

                    <div class="rmc-empty" v-else-if="pending">
                        <p>Загружаем каталог…</p>
                    </div>
                    <div class="rmc-empty" v-else>
                        <p>По этим условиям ничего не нашлось.</p>
                        <button type="button" class="rmc-reset" @click="resetFilters">Сбросить фильтры</button>
                    </div>

                    <nav class="rmc-pages" aria-label="Страницы каталога" v-if="pages > 1">
                        <button type="button" aria-label="Предыдущая страница" :disabled="page <= 1" @click="page--">
                            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round" class="lucide lucide-chevron-left">
                                <path d="m15 18-6-6 6-6"></path>
                            </svg>
                        </button>
                        <button type="button" :class="{ 'rmc-page-active': page === 1 }" @click="page = 1">1</button>
                        <button type="button" v-for="n in pages" :key="n" v-show="n > 1 && n < pages && Math.abs(n - page) <= 1"
                                :class="{ 'rmc-page-active': page === n }" @click="page = n">{{ n }}</button>
                        <span class="rmc-gap" v-if="pages > 3">…</span>
                        <button type="button" v-if="pages > 1" :class="{ 'rmc-page-active': page === pages }" @click="page = pages">
                            {{ pages }}
                        </button>
                        <button type="button" aria-label="Следующая страница" :disabled="page >= pages" @click="page++">
                            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round" class="lucide lucide-chevron-right">
                                <path d="m9 18 6-6-6-6"></path>
                            </svg>
                        </button>
                    </nav>
                </div>
            </div>
        </div>
</template>
<style scoped>
                    .rmc-root { position: relative; min-height: 100vh; padding-bottom: 18px;
                      font-family: 'Manrope','Inter',system-ui,sans-serif; color: #111A31; }
                    .rmc-bg { position: absolute; inset: 0; z-index: 0; overflow: hidden; }
                    .rmc-bg-veil { position: absolute; inset: 0;
                      background: linear-gradient(180deg, rgba(246,250,255,0.62), rgba(246,250,255,0.80)); }
                    .rmc-shell { position: relative; z-index: 1; width: min(1480px, 94%); margin: 0 auto; padding: 8px 0 10px; }

                    /* ── Герой: две колонки, чтобы не отъедать высоту у карточек ─────────────── */
                    .rmc-hero { display: grid; grid-template-columns: 1fr 1.9fr; gap: 34px; align-items: center; }
                    .rmc-h1 { margin: 0; font-family: 'Sora','Manrope',sans-serif; font-size: clamp(26px,2.5vw,36px);
                      font-weight: 800; letter-spacing: -0.03em; color: #0B1532; }
                    .rmc-lead { max-width: 440px; margin: 7px 0 0; font-size: 12px; line-height: 1.5; color: #4F5F77; }

                    .rmc-stats { display: grid; grid-template-columns: repeat(4, 1fr); gap: 11px; }
                    .rmc-stat { display: flex; align-items: center; gap: 10px; min-height: 50px; padding: 8px 11px;
                      border: 1px solid rgba(255,255,255,0.68); border-radius: 14px;
                      background: linear-gradient(145deg, rgba(255,255,255,0.72), rgba(231,242,253,0.52));
                      backdrop-filter: blur(22px); box-shadow: inset 0 1px 0 #fff, 0 10px 26px rgba(45,75,115,0.08); }
                    .rmc-stat-link { text-decoration: none; transition: transform .18s; }
                    .rmc-stat-link:hover { transform: translateY(-2px); }
                    .rmc-stat-icon { display: grid; place-items: center; width: 32px; height: 32px; flex: 0 0 32px;
                      border-radius: 10px; background: rgba(255,255,255,0.8); color: var(--accent); }
                    .rmc-stat b { display: block; font-size: 19px; font-weight: 800; color: var(--accent); letter-spacing: -0.02em; line-height: 1.1; }
                    .rmc-stat-small { font-size: 13.5px !important; }
                    .rmc-stat-label { display: block; margin-top: 2px; font-size: 10px; line-height: 1.3; color: #2E3E56; }

                    /* ── Панель фильтров ─────────────────────────────────────────────────────── */
                    .rmc-panel { margin-top: 8px; border: 1px solid rgba(255,255,255,0.68); border-radius: 17px;
                      background: linear-gradient(145deg, rgba(255,255,255,0.62), rgba(225,239,252,0.45));
                      backdrop-filter: blur(28px); box-shadow: inset 0 1px 0 #fff, 0 18px 44px rgba(45,75,115,0.10); overflow: hidden; }
                    .rmc-filters {display: grid; gap: 12px;
                      align-items: end; padding: 12px 13px 8px; }
                    .rmc-field { display: block; min-width: 0; }
                    .rmc-field > span { display: block; margin-bottom: 4px; font-size: 10.5px; color: #5B6C86; }
                    .rmc-search, .rmc-field select, .rmc-more-btn, .rmc-extra > select, .rmc-extra > .rmc-check {
                      height: 38px; border: 1px solid rgba(255,255,255,0.72); border-radius: 10px;
                      background: rgba(255,255,255,0.62); font-size: 12.5px; color: #111A31; }
                    .rmc-search { display: flex; align-items: center; gap: 9px; padding: 0 13px; color: #7A8AA3; min-width: 0; }
                    .rmc-search input { width: 100%; min-width: 0; border: 0; background: transparent; outline: 0; font: inherit; color: #111A31; }
                    .rmc-field select { width: 100%; padding: 0 11px; outline: 0; }
                    .rmc-more-btn { display: inline-flex; align-items: center; justify-content: center; gap: 7px;
                      cursor: pointer; font-weight: 600; color: #33445F; }
                    .rmc-extra { display: flex; flex-wrap: wrap; align-items: center; gap: 12px; padding: 0 14px 10px; }
                    .rmc-extra > select { min-width: 190px; padding: 0 11px; outline: 0; }
                    .rmc-check { display: inline-flex; align-items: center; gap: 8px; padding: 0 13px; color: #33445F; cursor: pointer; }
                    .rmc-check input { width: 15px; height: 15px; accent-color: #0B64F4; cursor: pointer; }
                    .rmc-reset { display: inline-flex; align-items: center; gap: 5px; cursor: pointer;
                      color: #0B64F4; font-size: 12px; font-weight: 600; background: transparent; border: 0; }

                    /* Семь вкладок в одну строку — как в референсе */
                    .rmc-tabs { display: grid; gap: 6px; padding: 0 13px 8px; }
                    .rmc-tab { display: flex; align-items: center; gap: 8px; min-height: 44px; padding: 6px 8px; cursor: pointer;
                      text-align: left; border: 1px solid rgba(255,255,255,0.55); border-radius: 11px;
                      background: rgba(255,255,255,0.38); color: #22314A; font: inherit; min-width: 0; }
                    .rmc-tab-active { border-color: var(--accent); background: rgba(255,255,255,0.72); box-shadow: 0 8px 22px rgba(65,105,165,0.08); }
                    .rmc-tab-icon { display: grid; place-items: center; width: 27px; height: 27px; flex: 0 0 27px;
                      border-radius: 8px; background: rgba(255,255,255,0.75); color: var(--accent); }
                    .rmc-tab-text { min-width: 0; font-size: 10px; font-weight: 700; line-height: 1.2;
                      display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
                    .rmc-tab-text small { display: block; margin-top: 3px; font-size: 10.5px; font-weight: 600; color: #47607F; }

                    /* ── Строка результатов ──────────────────────────────────────────────────── */
                    .rmc-resulthead { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;
                      gap: 8px; padding: 5px 4px 9px; font-size: 12px; color: #33445F; }
                    .rmc-resulthead b { color: var(--accent); }
                    .rmc-resultctl { display: flex; align-items: center; gap: 8px; color: #e8f3ff;}
                    .rmc-resultctl select { height: 32px; border: 1px solid rgba(255,255,255,0.72); border-radius: 8px;
                      background: rgba(255,255,255,0.62); padding: 0 10px; font: inherit; font-size: 12px; color: #111A31; outline: 0; }
                    .rmc-v { display: grid; place-items: center; width: 32px; height: 32px; cursor: pointer;
                      border: 1px solid rgba(255,255,255,0.72); border-radius: 8px; background: rgba(255,255,255,0.58); color: #5B6C86; }
                    .rmc-v-active { color: #fff; background: linear-gradient(135deg,#2B82FF,#075CF0); border-color: transparent; }

                    /* ── Карточки ────────────────────────────────────────────────────────────── */
                    .rmc-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
                    .rmc-list { display: flex; flex-direction: column; gap: 10px; }
                    .rmc-card { position: relative; display: flex; flex-direction: column; padding: 10px 12px 11px;
                      border: 1px solid rgba(255,255,255,0.68); border-radius: 15px;
                      background: linear-gradient(145deg, rgba(255,255,255,0.74), rgba(232,241,251,0.56));
                      backdrop-filter: blur(24px); box-shadow: inset 0 1px 0 #fff, 0 14px 32px rgba(41,70,112,0.10);
                      transition: transform .22s, box-shadow .22s; }
                    .rmc-card:hover { transform: translateY(-3px); box-shadow: inset 0 1px 0 #fff, 0 22px 44px rgba(38,69,118,0.15); }
                    /* Фото лежит на фоне карточки, а не в отдельной полосе — как на референсе */
                    /* Фото товара часто на белом фоне — без мягкой подложки оно теряется на карточке */
                    .rmc-visual { position: relative; height: 150px; margin: 1px 0 7px; border-radius: 12px;
                      background: radial-gradient(ellipse at center, rgba(255,255,255,0.95), rgba(255,255,255,0.18) 70%); }
                    .rmc-noimg { display: grid; place-items: center; height: 100%; font-size: 40px; opacity: 0.2; }
                    .rmc-badge { position: absolute; left: 11px; top: 11px; z-index: 2; padding: 4px 8px; border-radius: 999px;
                      background: rgba(235,244,255,0.92); color: #0B64F4; font-size: 9px; font-weight: 700; }
                    .rmc-badge-new { background: rgba(225,250,233,0.92); color: #15964F; }
                    .rmc-fav { position: absolute; right: 10px; top: 9px; z-index: 3; display: flex; gap: 6px; }
                    .rmc-body { display: flex; flex-direction: column; flex: 1; min-width: 0; }
                    .rmc-body h3 { margin: 0; font-size: 14px; font-weight: 800; line-height: 1.2; color: #0B1532;
                      display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
                    .rmc-stretch { text-decoration: none; color: inherit; }
                    .rmc-stretch::after { content: ''; position: absolute; inset: 0; z-index: 1; }
                    .rmc-maker { margin: 3px 0 0; font-size: 10px; color: #5D6D84; }
                    .rmc-desc { margin: 5px 0 6px; font-size: 10.5px; line-height: 1.38; color: #46566F;
                      display: -webkit-box; -webkit-box-orient: vertical; -webkit-line-clamp: 2; overflow: hidden; }
                    .rmc-tags { display: flex; gap: 5px; flex-wrap: wrap; max-height: 20px; overflow: hidden; }
                    .rmc-tags span { padding: 3px 6px; border-radius: 6px; background: rgba(245,248,253,0.8); font-size: 9.5px; color: #46566F; white-space: nowrap; }
                    .rmc-foot { display: flex; align-items: flex-end; justify-content: space-between; gap: 8px; margin-top: auto; padding-top: 6px; }
                    .rmc-price { color: var(--accent); font-size: 16.5px; font-weight: 800; letter-spacing: -0.02em; }
                    .rmc-sup { display: inline-flex; align-items: center; gap: 4px; margin-top: 4px; font-size: 10px; color: #52657F; }
                    .rmc-go { display: grid; place-items: center; width: 30px; height: 30px; flex: 0 0 30px; border-radius: 9px;
                      background: rgba(255,255,255,0.72); border: 1px solid rgba(255,255,255,0.85); color: #0B64F4; }

                    /* Список — то же содержимое строкой */
                    .rmc-card-row { flex-direction: row; align-items: center; gap: 14px; padding: 11px 13px; }
                    .rmc-card-row .rmc-visual { width: 190px; flex: 0 0 190px; height: 104px; margin: 0; }
                    .rmc-card-row .rmc-body { flex: 1; }
                    .rmc-card-row .rmc-desc { -webkit-line-clamp: 1; }
                    .rmc-card-row .rmc-foot { margin-top: 7px; padding-top: 0; }

                    .rmc-empty { display: grid; place-items: center; gap: 10px; padding: 48px 20px; color: #6B7A93;
                      border: 1px dashed rgba(255,255,255,0.8); border-radius: 15px; background: rgba(255,255,255,0.45); }
                    .rmc-empty p { margin: 0; font-size: 13px; }

                    .rmc-pages { display: flex; justify-content: center; align-items: center; gap: 7px; padding: 8px 0 2px; }
                    .rmc-pages button { display: grid; place-items: center; width: 32px; height: 32px; cursor: pointer;
                      border: 1px solid rgba(255,255,255,0.72); border-radius: 9px; background: rgba(255,255,255,0.58);
                      font: inherit; font-size: 12.5px; color: #33445F; }
                    .rmc-pages button:disabled { opacity: 0.4; cursor: default; }
                    .rmc-page-active { color: #fff !important; background: linear-gradient(135deg,#2B82FF,#075CF0) !important; border-color: transparent !important; font-weight: 700; }
                    .rmc-gap { color: #7A8AA3; }
                    .rmc-filter-panel__sidebar_left {
                        width: 50rem;
                      }

                    @media (max-width: 1280px) {
                      .rmc-tabs { grid-template-columns: repeat(4, minmax(0, 1fr)); }
                      .rmc-filter-panel {
                        flex-direction: column;
                      }
                      .rmc-filter-panel__sidebar_left {
                        width: 100%;
                      }

                    }
                    @media (max-width: 1100px) {
                      .rmc-hero { grid-template-columns: 1fr; gap: 18px; }
                      .rmc-filters { grid-template-columns: 1fr 1fr; }
                      .rmc-search { grid-column: 1 / -1; }
                      .rmc-grid { grid-template-columns: repeat(2, 1fr); }

                    }
                    @media (max-width: 720px) {
                      .rmc-shell { width: calc(100% - 20px); }
                      .rmc-stats { grid-template-columns: 1fr 1fr; }
                      .rmc-filters { grid-template-columns: 1fr; }
                      .rmc-tabs { grid-template-columns: 1fr 1fr; }
                      .rmc-grid { grid-template-columns: 1fr; }
                      .rmc-resulthead { align-items: flex-start; }
                      .rmc-card-row { flex-direction: column; align-items: stretch; }
                      .rmc-card-row .rmc-visual { width: 100%; flex: none; height: 150px; }
                    }
                
/* Добавлено к исходной вёрстке страницы. */
.rmc-visual--initials {
  display: grid;
  place-items: center;
  font-weight: 700;
  letter-spacing: .04em;
  color: #0568FF;
  background: linear-gradient(135deg, #EEF4FF 0%, #F7FAFF 100%);
}

.rmc-reset {
  margin-top: 10px;
  padding: 7px 12px;
  font: inherit;
  font-size: 13px;
  color: #0568FF;
  background: #fff;
  border: 1px solid #0568FF;
  border-radius: 8px;
  cursor: pointer;
}

.rmc-reset:hover {
  background: #0568FF;
  color: #fff;
}
</style>