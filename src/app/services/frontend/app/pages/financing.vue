<script setup lang="ts">
useHead({ title: 'Финансирование роботизации' })

// Страница считает на настоящих данных: справочник параметров объекта,
// цены позиций каталога и модель экономики на бэкенде. Раньше здесь был
// статичный макет — четыре карточки и таблица, в которых нельзя было
// ничего изменить и неоткуда было взяться цифрам.
//
// Считает бэкенд, а не форма: POST /scenarios/{id}/calculate отдаёт
// стоимость владения по трём сценариям, разбивку CAPEX/OPEX, денежный
// поток по годам и анализ чувствительности. Лизинга и аренды в модели
// нет — сравнение таких схем осталось качественным, без выдуманных сумм.

const { $fetchApi } = useNuxtApp()
const auth = useAuthStore()

// Иллюстрации схем лежат в assets, а не в public: путь вида
// /img/buy.avif отдавал бы 404. Через импорт Nuxt собирает их с хешем в
// имени и отдаёт по правильному адресу сам.
import buyImg from '~/assets/img/buy.avif'
import leaseImg from '~/assets/img/lease.avif'
import rentImg from '~/assets/img/rent.avif'
import raasImg from '~/assets/img/raas.avif'

const SCHEMES = [
  { t: 'Покупка', img: buyImg, d: 'Роботы на балансе предприятия', calc: 'считается' },
  { t: 'Лизинг', img: leaseImg, d: 'Платёж банку, актив ваш', calc: 'не считается' },
  { t: 'Аренда', img: rentImg, d: 'Робот на срок, без владения', calc: 'не считается' },
  { t: 'RaaS', img: raasImg, d: 'Роботизация как услуга', calc: 'считается' },
]

type DictItem = { code: string; name: string }
type Param = {
  code: string
  name: string
  unit: string | null
  value_type: string
  min_value: number | null
  max_value: number | null
  default_value: number | null
  default_text: string | null
  options: unknown
  required: boolean
}
type Line = { id: string; name: string; price: number; qty: number; type: string | null }

const objectTypes = ref<DictItem[]>([])
const processes = ref<DictItem[]>([])
const params = ref<Param[]>([])
const values = ref<Record<string, any>>({})
const requiredCodes = ref<string[]>([])
const catalog = ref<any[]>([])

const objectType = ref('warehouse')
const chosenProcesses = ref<string[]>([])
const lines = ref<Line[]>([])
const horizon = ref(5)
const search = ref('')

const projectId = ref<string | null>(null)
const scenarioId = ref<number | null>(null)
const result = ref<any>(null)
const busy = ref(false)
const loadError = ref<string | null>(null)
const calcError = ref<string | null>(null)
const problems = ref<string[]>([])

const money = (v: any, digits = 0) =>
  v === null || v === undefined
    ? '—'
    : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: digits }).format(v) + ' ₽'
const plain = (v: any, digits = 0) =>
  v === null || v === undefined
    ? '—'
    : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: digits }).format(v)
const pct = (v: any) => (v === null || v === undefined ? '—' : plain(v, 1) + ' %')
// Окончание согласуется с числом: «0,6 года», «3 года», «5 лет».
const plural = (count: number, one: string, few: string, many: string) => {
  const c = Math.round(Math.abs(Number(count) || 0))
  const tail100 = c % 100
  const tail10 = c % 10
  const word = 11 <= tail100 && tail100 <= 14 ? many : tail10 === 1 ? one : 2 <= tail10 <= 4 ? few : many
  return word
}

// ── Справочники ────────────────────────────────────────────────────────────
// Загружаются один раз при входе на страницу: пользователь смотрит схемы
// и сравнение без авторизации, поэтому пустые справочники сломали бы вид
// даже гостю.
onMounted(async () => {
  try {
    const [types, procs, list] = await Promise.all([
      $fetchApi<DictItem[]>('/api/v1/object-types'),
      $fetchApi<DictItem[]>('/api/v1/processes'),
      $fetchApi<any>('/api/v1/catalog?limit=400&min_completeness=1'),
    ])
    objectTypes.value = Array.isArray(types) ? types : (types?.items ?? [])
    processes.value = Array.isArray(procs) ? procs : (procs?.items ?? [])
    catalog.value = (list?.items ?? []).filter((s: any) => s.unit_price_rub != null)
    await loadObjectType(objectType.value)
  } catch (e: any) {
    loadError.value = e?.data?.message ?? e?.message ?? 'Не удалось загрузить справочники.'
  }
})

// Параметры и умолчания зависят от типа объекта. Значения по умолчанию
// заполняем целиком: без них расчёт лишён базы, а спрашивать 42 поля
// невозможно. Показаны только обязательные — остальные участвуют через
// умолчания.
async function loadObjectType(code: string) {
  objectType.value = code
  const [plist, defs] = await Promise.all([
    $fetchApi<Param[]>(`/api/v1/object-types/${code}/parameters`),
    $fetchApi<any>(`/api/v1/object-types/${code}/parameters/defaults`),
  ])
  params.value = Array.isArray(plist) ? plist : (plist?.items ?? [])
  values.value = { ...(defs?.values ?? {}) }
  requiredCodes.value = defs?.required_parameters ?? []
  chosenProcesses.value = []
}

const shownParams = computed(() =>
  requiredCodes.value.length
    ? params.value.filter((p) => requiredCodes.value.includes(p.code))
    : params.value,
)

// Перечисления приходят списком строк, а администратор может завести
// вариант с подписью — понимаем оба вида, иначе выбор был бы пустым.
function enumOptions(param: Param): string[] {
  const out: string[] = []
  for (const o of param.options ?? []) {
    if (typeof o === 'string') out.push(o)
    else if (o && typeof o === 'object') {
      const v = (o as any).value ?? (o as any).label
      if (v != null) out.push(String(v))
    }
  }
  return out
}

// ── Оборудование ───────────────────────────────────────────────────────────
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const base = q
    ? catalog.value.filter((s) => (s.name ?? '').toLowerCase().includes(q))
    : catalog.value
  return base.slice(0, 40)
})

function addLine(s: any) {
  const found = lines.value.find((l) => l.id === s.id)
  if (found) {
    found.qty = Math.min(found.qty + 1, 1000)
    return
  }
  lines.value.push({
    id: s.id,
    name: s.name,
    price: Number(s.unit_price_rub),
    qty: 1,
    type: s.solution_type?.name ?? null,
  })
}
const dropLine = (id: string) => {
  lines.value = lines.value.filter((l) => l.id !== id)
}
const equipmentTotal = computed(() =>
  lines.value.reduce((sum, l) => sum + l.price * l.qty, 0),
)

// ── Расчёт ─────────────────────────────────────────────────────────────────
// Проект и сценарий создаются один раз и переиспользуются: иначе каждый
// клик «Рассчитать» оставлял бы в базе новую пару записей.
async function calculate() {
  calcError.value = null
  problems.value = []
  if (!lines.value.length) {
    calcError.value = 'Выберите хотя бы одну позицию оборудования — считать нечего.'
    return
  }
  busy.value = true
  try {
    const body = {
      name: 'Расчёт на платформе',
      object_type: objectType.value,
      parameters: values.value,
      process_codes: chosenProcesses.value,
    }
    if (!projectId.value) {
      const proj = await $fetchApi<any>('/api/v1/projects', { method: 'POST', body })
      projectId.value = proj.id
    } else {
      await $fetchApi(`/api/v1/projects/${projectId.value}`, {
        method: 'PATCH',
        body: {
          parameters: values.value,
          process_codes: chosenProcesses.value,
        },
      })
    }
    const items = lines.value.map((l) => ({ solution_id: l.id, quantity: l.qty }))
    if (!scenarioId.value) {
      const scen = await $fetchApi<any>(`/api/v1/projects/${projectId.value}/scenarios`, {
        method: 'POST',
        body: { name: 'Покупка', kind: 'purchase', items, horizon_years: horizon.value },
      })
      scenarioId.value = scen.id
    } else {
      await $fetchApi(`/api/v1/projects/${projectId.value}/scenarios/${scenarioId.value}`, {
        method: 'PATCH',
        body: { items, horizon_years: horizon.value },
      })
    }
    // persist=false: расчёт — предпросмотр, снимок нужен только в истории
    // проекта, а не на каждый пересчёт формы.
    result.value = await $fetchApi<any>(
      `/api/v1/scenarios/${scenarioId.value}/calculate?persist=false&with_sensitivity=true`,
      { method: 'POST' },
    )
  } catch (e: any) {
    calcError.value = e?.data?.message ?? e?.message ?? 'Не удалось выполнить расчёт.'
    problems.value = e?.data?.details?.problems ?? []
  } finally {
    busy.value = false
  }
}

// ── Представление результата ────────────────────────────────────────────────
const MODEL_LABEL: Record<string, string> = {
  baseline: 'Без роботизации',
  purchase: 'Покупка',
  raas: 'RaaS',
}
const MODEL_HINT: Record<string, string> = {
  baseline: 'текущие расходы без роботов',
  purchase: 'роботы на балансе предприятия',
  raas: 'платёж за сервис, без CAPEX',
}

const tcoRows = computed(() => {
  const sc = result.value?.tco?.scenarios
  if (!sc) return []
  return Object.keys(MODEL_LABEL)
    .filter((k) => sc[k])
    .map((k) => ({
      key: k,
      label: MODEL_LABEL[k],
      hint: MODEL_HINT[k],
      total: sc[k].total,
      annual: sc[k].annual,
      setup: sc[k].setup,
      residual: sc[k].residual_labor_annual,
      breakdown: sc[k].breakdown ?? {},
      best: result.value.tco.best_option === k,
    }))
})

const purchase = computed(() => result.value?.purchase ?? null)
const raas = computed(() => result.value?.raas ?? null)
// Коммерческие условия RaaS (платёж, вводный взнос, срок, доступность)
// лежат внутри блока сценария под ключом «raas», а не в самом блоке:
// верхний уровень res.raas — это расчёт по сценарию RaaS с теми же
// capex/opex/payback, что и у покупки.
const raasTerms = computed(() => raas.value?.raas ?? null)
const meta = computed(() => result.value?.meta ?? null)

const capexRows = computed(() => {
  const c = purchase.value?.capex
  if (!c) return []
  return [
    { label: 'Оборудование', value: c.equipment },
    { label: 'Программное обеспечение', value: c.software },
    { label: 'Внедрение', value: c.integration },
    { label: 'Пусконаладка', value: c.commissioning },
    { label: 'Обучение персонала', value: c.training },
    { label: 'Зарядные станции', value: c.charging_stations },
  ].filter((r) => r.value)
})

const opexRows = computed(() => {
  const o = purchase.value?.opex
  if (!o) return []
  return [
    { label: 'Сервис и ТО', value: o.service },
    { label: 'Лицензии', value: o.licenses },
    { label: 'Электроэнергия', value: o.energy },
    { label: 'Расходные материалы', value: o.consumables },
    { label: 'Сопровождение внедрения', value: o.integration_support },
    { label: 'Страхование', value: o.insurance },
    { label: 'Замена АКБ', value: o.battery_replacement },
  ].filter((r) => r.value)
})

// Денежный поток по годам: берём кумулятивный денежный поток, а не
// бухгалтерский — амортизация не отвлекает средств и в окупаемости не
// участвует, это оговорено в note модели.
const scheduleRows = computed(() => purchase.value?.schedule ?? [])

// Чувствительность показываем отклонением от базового расчёта, а не самим
// годовым эффектом. Годовой эффект у всех пяти точек отличается мало, и по
// нему не видно, насколько допущение важно: полосы выходили одинаковыми.
// Отклонение от точки «как посчитано» показывает, в какую сторону и
// насколько сильно уводит допущение — это и есть смысл анализа.
const sensitivityRows = computed(() => {
  const list = result.value?.sensitivity
  if (!Array.isArray(list)) return []
  return list.map((s: any) => {
    const pts: any[] = Array.isArray(s.points) ? s.points : []
    const base = Number(pts.find((p) => Number(p.factor) === 1)?.annual_effect ?? 0)
    const deltas = pts.map((p) => Number(p.annual_effect ?? 0) - base)
    const max = Math.max(...deltas.map(Math.abs), 1)
    return {
      key: s.key,
      label: s.label,
      spread: s.effect_spread,
      base,
      points: pts.map((p, i) => ({
        pct: (Number(p.factor) - 1) * 100,
        effect: p.annual_effect,
        delta: deltas[i],
        // Половина высоты — максимум: полосы растут вверх и вниз от базовой
        // линии. Делим на два, потому что каждая половина занимает 50%.
        up: deltas[i] > 0 ? Math.round((deltas[i] / max) * 50) : 0,
        down: deltas[i] < 0 ? Math.round((Math.abs(deltas[i]) / max) * 50) : 0,
      })),
    }
  })
})
</script>

<template>
    <section class="relative isolate overflow-hidden" style="margin-top: -76px;">
        <div class="mx-auto fin-dash-wrap" style="max-width: 1440px; padding: 106px clamp(20px, 4vw, 40px) 40px;">
            <div style="max-width: 620px; margin-bottom: 18px;">
                <h1 style="display: block; margin: 0; font-size: clamp(30px, 3.6vw, 52px); line-height: 1.05; letter-spacing: -0.03em; font-weight: 800; color: rgb(11, 22, 38);">
                    Подберём оптимальное финансирование для проекта</h1>
                <p style="display: block; margin: 16px 0 0; max-width: 560px; font-size: clamp(14px, 1.4vw, 17px); line-height: 1.5; color: rgb(76, 88, 106);">
                    Сравним покупку и RaaS с вариантом без роботов. Расчёт идёт по ценам каталога
                    и справочнику параметров объекта.</p>
            </div>

            <p v-if="loadError" class="fin-note fin-note--bad">{{ loadError }}</p>

            <!-- Вход нужен: расчёт создаёт проект и снимок, а бэкенд
                 требует пользователя. Гость видит схемы и сравнение ниже. -->
            <div v-if="!auth.isAuthenticated" class="fin-card fin-card--gate">
                <div>
                    <h2 style="margin: 0 0 6px; font-size: 17px; color: #0B1626;">Войдите, чтобы рассчитать</h2>
                    <p style="margin: 0; font-size: 13px; color: #4C586A; line-height: 1.45;">
                        Расчёт сохраняет проект и состав оборудования в вашем кабинете.
                        Демо-доступ: <b>user@example.com</b> / <b>demo12345</b>.</p>
                </div>
                <div style="display: flex; gap: 8px; flex-shrink: 0;">
                    <NuxtLink class="fin-btn fin-btn--ghost" to="/login">Войти</NuxtLink>
                    <NuxtLink class="fin-btn" to="/register">Регистрация</NuxtLink>
                </div>
            </div>

            <div v-else class="fin-grid">
                <!-- Форма -->
                <section class="fin-card">
                    <h2 class="fin-h">Объект</h2>
                    <div class="fin-otypes">
                        <button v-for="t in objectTypes" :key="t.code" type="button"
                                class="fin-otype" :class="{ 'fin-otype--on': objectType === t.code }"
                                @click="loadObjectType(t.code)">
                            {{ t.name }}
                        </button>
                    </div>

                    <template v-if="processes.length">
                        <h2 class="fin-h">Процессы</h2>
                        <p class="fin-hint">От них зависит, какой эффект считает модель.</p>
                        <div class="fin-chips">
                            <button v-for="p in processes" :key="p.code" type="button"
                                    class="fin-chip" :class="{ 'fin-chip--on': chosenProcesses.includes(p.code) }"
                                    @click="chosenProcesses = chosenProcesses.includes(p.code)
                                        ? chosenProcesses.filter((c) => c !== p.code)
                                        : [...chosenProcesses, p.code]">
                                {{ p.name }}
                            </button>
                        </div>
                    </template>

                    <h2 class="fin-h">Параметры объекта</h2>
                    <p class="fin-hint">
                        Обязательные поля. Остальные {{ Math.max(0, params.length - shownParams.length) }}
                        берутся из справочника автоматически.
                    </p>
                    <div class="fin-params">
                        <label v-for="p in shownParams" :key="p.code" class="fin-param">
                            <span class="fin-param__name">
                                {{ p.name }}
                                <i v-if="p.unit" class="fin-param__unit">{{ p.unit }}</i>
                            </span>
                            <select v-if="p.value_type === 'enum'" v-model="values[p.code]"
                                    class="fin-input">
                                <option v-for="o in enumOptions(p)" :key="o" :value="o">{{ o }}</option>
                            </select>
                            <input v-else v-model="values[p.code]" class="fin-input" type="number"
                                   step="any" :min="p.min_value ?? undefined" :max="p.max_value ?? undefined">
                        </label>
                    </div>

                    <h2 class="fin-h">Оборудование</h2>
                    <p class="fin-hint">Позиции и цены берутся из каталога.</p>
                    <input v-model="search" class="fin-input fin-input--search"
                           type="search" placeholder="Поиск по названию, например Ronavi">
                    <ul v-if="filtered.length" class="fin-picker">
                        <li v-for="s in filtered" :key="s.id">
                            <button type="button" class="fin-pick" @click="addLine(s)">
                                <span class="fin-pick__name">{{ s.name }}</span>
                                <span class="fin-pick__type">{{ s.solution_type?.name }}</span>
                                <span class="fin-pick__price">{{ money(s.unit_price_rub) }}</span>
                            </button>
                        </li>
                    </ul>
                    <p v-else class="fin-hint">Ничего не найдено.</p>

                    <h2 class="fin-h">Состав сценария</h2>
                    <div v-if="lines.length" class="fin-lines">
                        <div v-for="l in lines" :key="l.id" class="fin-line">
                            <span class="fin-line__name">
                                {{ l.name }}
                                <i class="fin-line__price">{{ money(l.price) }}</i>
                            </span>
                            <input v-model.number="l.qty" class="fin-input fin-input--qty" type="number"
                                   min="1" max="1000">
                            <button type="button" class="fin-line__drop" title="Убрать" @click="dropLine(l.id)">×</button>
                        </div>
                        <p class="fin-sum">Итого оборудования: <b>{{ money(equipmentTotal) }}</b></p>
                    </div>
                    <p v-else class="fin-hint">Пока пусто. Выберите позиции выше — без них расчёт невозможен.</p>

                    <label class="fin-horizon">
                        <span>Горизонт расчёта: <b>{{ horizon }} лет</b></span>
                        <input v-model.number="horizon" type="range" min="1" max="30" step="1">
                    </label>

                    <button type="button" class="fin-btn fin-btn--wide" :disabled="busy" @click="calculate">
                        {{ busy ? 'Считаем…' : 'Рассчитать' }}
                    </button>
                    <p v-if="calcError" class="fin-note fin-note--bad">
                        {{ calcError }}
                        <span v-for="p in problems" :key="p" class="fin-problem">{{ p }}</span>
                    </p>
                </section>

                <!-- Результат -->
                <section class="fin-card">
                    <p v-if="!result" class="fin-empty">
                        Заполните параметры и нажмите «Рассчитать» — покажем стоимость владения
                        по трём сценариям, разбивку затрат и чувствительность к допущениям.
                    </p>

                    <template v-else>
                        <h2 class="fin-h">
                            Стоимость владения за {{ result.tco.horizon_years }} лет
                        </h2>
                        <p v-if="result.tco.note" class="fin-hint">{{ result.tco.note }}</p>

                        <table class="fin-tco">
                            <thead>
                            <tr>
                                <th scope="col">Сценарий</th>
                                <th scope="col">Запуск</th>
                                <th scope="col">В год</th>
                                <th scope="col">За {{ result.tco.horizon_years }} лет</th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="r in tcoRows" :key="r.key" :class="{ 'fin-best': r.best }">
                                <th scope="row">
                                    {{ r.label }}
                                    <i class="fin-tco__hint">{{ r.hint }}</i>
                                    <b v-if="r.best" class="fin-badge">выгоднее</b>
                                </th>
                                <td>{{ money(r.setup) }}</td>
                                <td>{{ money(r.annual) }}</td>
                                <td class="fin-tco__total">{{ money(r.total) }}</td>
                            </tr>
                            </tbody>
                        </table>
                        <p v-if="result.tco.saving_vs_purchase" class="fin-note">
                            Экономия против покупки:
                            <b v-for="(v, k) in result.tco.saving_vs_purchase" :key="k"
                               class="fin-note__item">{{ MODEL_LABEL[k] }} — {{ money(v) }}</b>
                        </p>

                        <template v-if="purchase">
                            <h2 class="fin-h">Единовременные затраты, покупка</h2>
                            <div class="fin-split">
                                <ul class="fin-money">
                                    <li v-for="r in capexRows" :key="r.label">
                                        <span>{{ r.label }}</span><b>{{ money(r.value) }}</b>
                                    </li>
                                    <li class="fin-money--total">
                                        <span>Всего CAPEX</span><b>{{ money(purchase.capex.total) }}</b>
                                    </li>
                                </ul>
                                <ul class="fin-money">
                                    <li v-for="r in opexRows" :key="r.label">
                                        <span>{{ r.label }}</span><b>{{ money(r.value) }}</b>
                                    </li>
                                    <li class="fin-money--total">
                                        <span>Всего OPEX за год</span><b>{{ money(purchase.opex.total) }}</b>
                                    </li>
                                </ul>
                            </div>

                            <h2 class="fin-h">Эффект и окупаемость</h2>
                            <div class="fin-kpi">
                                <div class="fin-kpi__cell">
                                    <span>Экономия ФОТ в год</span><b>{{ money(purchase.effect.labor_saving) }}</b>
                                </div>
                                <div class="fin-kpi__cell">
                                    <span>Чистый эффект в год</span>
                                    <b :class="{ 'fin-neg': purchase.effect.net_annual_cash < 0 }">
                                        {{ money(purchase.effect.net_annual_cash) }}
                                    </b>
                                </div>
                                <div class="fin-kpi__cell">
                                    <span>Окупаемость</span>
                                    <b v-if="purchase.payback.cash_payback_years === null">не окупается</b>
                                    <b v-else>
                                        {{ plain(purchase.payback.cash_payback_years, 1) }}
                                        {{ plural(purchase.payback.cash_payback_years, 'год', 'года', 'лет') }}
                                    </b>
                                </div>
                                <div class="fin-kpi__cell">
                                    <span>ROI за {{ result.tco.horizon_years }} лет</span>
                                    <b :class="{ 'fin-neg': purchase.roi_pct < 0 }">{{ pct(purchase.roi_pct) }}</b>
                                </div>
                            </div>
                            <p v-if="purchase.payback.note" class="fin-hint">{{ purchase.payback.note }}</p>

                            <h2 class="fin-h">Денежный поток по годам</h2>
                            <table class="fin-years">
                                <thead>
                                <tr>
                                    <th scope="col">Год</th>
                                    <th scope="col">OPEX</th>
                                    <th scope="col">Экономия ФОТ</th>
                                    <th scope="col">За год</th>
                                    <th scope="col">Накопленным итогом</th>
                                </tr>
                                </thead>
                                <tbody>
                                <tr v-for="y in scheduleRows" :key="y.year">
                                    <th scope="row">{{ y.year }}</th>
                                    <td>{{ money(y.opex) }}</td>
                                    <td>{{ money(y.labor_saving) }}</td>
                                    <td :class="{ 'fin-neg': y.net_annual_cash < 0 }">{{ money(y.net_annual_cash) }}</td>
                                    <td :class="{ 'fin-neg': y.cumulative_cash < 0 }">{{ money(y.cumulative_cash) }}</td>
                                </tr>
                                </tbody>
                            </table>
                        </template>

                        <template v-if="raasTerms">
                            <h2 class="fin-h">RaaS</h2>
                            <div class="fin-kpi">
                                <div class="fin-kpi__cell">
                                    <span>Платёж в год</span><b>{{ money(raasTerms.annual_payment) }}</b>
                                </div>
                                <div class="fin-kpi__cell">
                                    <span>Вводный платёж</span><b>{{ money(raasTerms.setup_fee) }}</b>
                                </div>
                                <div class="fin-kpi__cell">
                                    <span>Срок договора</span>
                                    <b v-if="raasTerms.term_months">
                                        {{ plain(raasTerms.term_months / 12, 1) }}
                                        {{ plural(raasTerms.term_months / 12, 'год', 'года', 'лет') }}
                                    </b>
                                    <b v-else>—</b>
                                </div>
                                <div class="fin-kpi__cell">
                                    <span>Экономия против покупки за срок договора</span>
                                    <b :class="{ 'fin-neg': raasTerms.delta_vs_purchase < 0 }">
                                        {{ money(raasTerms.delta_vs_purchase) }}
                                    </b>
                                </div>
                            </div>
                            <p class="fin-hint">
                                В платёж входит обслуживание, ПО и замена АКБ;
                                гарантированная доступность по договору —
                                {{ pct(raasTerms.min_availability * 100) }}. Сравнение с покупкой —
                                за {{ plural(raasTerms.term_months / 12, 'год', 'года', 'лет') }},
                                тогда как таблица выше считает за {{ result.tco.horizon_years }} лет.
                            </p>
                            <ul v-if="raasTerms.notes?.length" class="fin-warn">
                                <li v-for="(ntxt, i) in raasTerms.notes" :key="i">{{ ntxt }}</li>
                            </ul>
                        </template>

                        <template v-if="sensitivityRows.length">
                            <h2 class="fin-h">Чувствительность к допущениям</h2>
                            <p class="fin-hint">
                                Отклонение годового эффекта от базового расчёта
                                ({{ money(sensitivityRows[0].base) }}), если допущение платформы
                                меняется на ±30%. Вверх — эффект выше базового, вниз — ниже.
                                Чем длиннее полоса, тем сильнее результат зависит от этого допущения.
                            </p>
                            <div v-for="s in sensitivityRows" :key="s.key" class="fin-sens">
                                <div class="fin-sens__head">
                                    <span>{{ s.label }}</span>
                                    <i>разброс {{ money(s.spread) }}</i>
                                </div>
                                <div class="fin-sens__bars">
                                    <div v-for="pt in s.points" :key="pt.pct" class="fin-sens__point">
                                        <span class="fin-sens__delta">{{ pt.pct > 0 ? '+' : '' }}{{ plain(pt.pct, 0) }}%</span>
                                        <div class="fin-sens__bar">
                                            <i class="fin-sens__up" :style="{ height: pt.up + '%' }"></i>
                                            <i class="fin-sens__down" :style="{ height: pt.down + '%' }"></i>
                                        </div>
                                        <span class="fin-sens__value" :class="{ 'fin-neg': pt.delta < 0 }">
                                            {{ pt.delta >= 0 ? '+' : '−' }}{{ money(Math.abs(pt.delta)) }}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        </template>

                        <template v-if="result.warnings?.length">
                            <h2 class="fin-h">Оговорки к расчёту</h2>
                            <ul class="fin-warn">
                                <li v-for="(wmsg, i) in result.warnings" :key="i">{{ wmsg }}</li>
                            </ul>
                        </template>

                        <p v-if="meta?.duration_ms != null" class="fin-hint">
                            Модель {{ meta.model_version }}, расчёт за {{ meta.duration_ms }} мс.
                        </p>
                    </template>
                </section>
            </div>

            <!-- Справочная часть: какие схемы бывают и чем отличаются.
                 Числовое сравние выше считает только покупку и RaaS —
                 лизинга и аренды в модели нет, домысливать их суммы
                 нельзя, поэтому здесь они описаны словами. -->
            <div class="fin-dash-grid">
                <div class="fin-area-left">
                    <div class="fin-area-schemes"
                         style="background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1); border-radius: 16px; box-shadow: rgba(31, 73, 136, 0.08) 0px 16px 45px; backdrop-filter: blur(8px); padding: 16px;">
                        <p style="font-size: 13px; font-weight: 700; color: rgb(11, 22, 38); margin: 0 0 8px;">
                            Схемы финансирования</p>
                        <div class="fin-schemes-inner">
                            <article v-for="s in SCHEMES" :key="s.t" class="fin-scheme-mini"
                                     :class="{ 'fin-scheme-mini--on': s.calc === 'считается' }">
                                <div class="fin-scheme-mini__img">
                                    <img :src="s.img" :alt="s.t" loading="lazy" decoding="async">
                                </div>
                                <h3 style="font-size: 13.5px; font-weight: 700; margin: 0 0 2px; color: rgb(11, 22, 38);">
                                    {{ s.t }}</h3>
                                <p style="font-size: 10.5px; line-height: 1.35; color: rgb(76, 88, 106); margin: 0 0 6px;">
                                    {{ s.d }}</p>
                                <span class="fin-scheme-mini__flag">{{ s.calc }}</span>
                            </article>
                        </div>
                    </div>
                    <div class="fin-area-request"
                         style="background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1); border-radius: 16px; box-shadow: rgba(31, 73, 136, 0.08) 0px 16px 45px; backdrop-filter: blur(8px); padding: 18px;">
                        <h2 style="font-size: 18px; font-weight: 800; line-height: 1.12; margin: 0 0 7px; color: rgb(11, 22, 38); letter-spacing: -0.01em;">
                            Готовы начать роботизацию?</h2>
                        <p style="font-size: 11px; color: rgb(76, 88, 106); line-height: 1.4; margin: 0 0 12px;">
                            Подготовим варианты финансирования под ваш проект.</p>
                        <NuxtLink to="/robot-selection" class="fin-btn">
                            Подбор роботов
                            <svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round" aria-hidden="true">
                                <path d="M5 12h14"></path>
                                <path d="m12 5 7 7-7 7"></path>
                            </svg>
                        </NuxtLink>
                    </div>
                </div>
                <div class="fin-area-compare"
                     style="background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(36, 83, 151, 0.1); border-radius: 16px; box-shadow: rgba(31, 73, 136, 0.08) 0px 16px 45px; backdrop-filter: blur(8px); padding: 14px; display: flex; flex-direction: column;">
                    <p style="font-size: 13px; font-weight: 700; color: rgb(11, 22, 38); margin: 0 0 4px;">
                        Чем отличаются схемы</p>
                    <p style="font-size: 10px; line-height: 1.4; color: rgb(76, 88, 106); margin: 0 0 8px;">
                        Качественное сравнение. Суммы по покупке и RaaS считает калькулятор выше.</p>
                    <div class="fin-cmp-scroll">
                        <table class="fin-cmp-table">
                            <caption class="sr-only">Сравнение моделей финансирования роботизации</caption>
                            <thead>
                            <tr>
                                <th scope="col">Критерий</th>
                                <th scope="col">Покупка</th>
                                <th scope="col">Лизинг</th>
                                <th scope="col">Аренда</th>
                                <th scope="col">RaaS<span class="fin-cmp__sub">робот как услуга</span></th>
                            </tr>
                            </thead>
                            <tbody>
                            <tr v-for="row in [
                                { c: 'В собственности клиента', v: ['✓', 'После выкупа', '✕', '✕'] },
                                { c: 'Низкий стартовый платёж', v: ['✕', '✓', '✓', '✓'] },
                                { c: 'Подходит для пилота', v: ['✕', 'Частично', '✓', '✓'] },
                                { c: 'Сервис и поддержка включены', v: ['Отдельно', 'Частично', '✓', '✓'] },
                                { c: 'Оплата за результат', v: ['✕', '✕', 'Иногда', '✓'] },
                                { c: 'Быстрый старт', v: ['Средне', 'Средне', 'Быстро', 'Быстро'] },
                                { c: 'Риск простоя', v: ['Клиент', 'Частично', 'Поставщик', 'Поставщик'] },
                            ]" :key="row.c">
                                <th scope="row">{{ row.c }}</th>
                                <td v-for="(cell, i) in row.v" :key="i"
                                    :class="{ 'fin-yes': cell === '✓', 'fin-no': cell === '✕' }">
                                    {{ cell }}
                                </td>
                            </tr>
                            </tbody>
                        </table>
                    </div>
                    <p style="margin: 10px 0 0; padding-top: 8px; border-top: 1px solid rgba(36, 83, 151, 0.1); font-size: 10px; line-height: 1.45; color: rgb(76, 88, 106);">
                        Условия зависят от типа проекта, оборудования, срока и финансового профиля компании.</p>
                </div>
            </div>
        </div>
    </section>
</template>

<style scoped>
.fin-card {
    background: rgba(255, 255, 255, 0.94);
    border: 1px solid rgba(36, 83, 151, 0.1);
    border-radius: 16px;
    box-shadow: rgba(31, 73, 136, 0.08) 0px 16px 45px;
    backdrop-filter: blur(8px);
    padding: 18px;
}

.fin-card--gate { display: flex; align-items: center; justify-content: space-between; gap: 16px; flex-wrap: wrap; }

.fin-grid { display: grid; grid-template-columns: minmax(0, 1fr) minmax(0, 1.05fr); gap: 16px; align-items: start; }

.fin-h { margin: 20px 0 4px; font-size: 13px; font-weight: 700; color: #0B1626; }
.fin-card > .fin-h:first-child { margin-top: 0; }
.fin-hint { margin: 0 0 8px; font-size: 10.5px; line-height: 1.4; color: #4C586A; }

.fin-otypes { display: flex; flex-wrap: wrap; gap: 6px; }
.fin-otype { padding: 7px 12px; border-radius: 9px; border: 1px solid #DCE5F2; background: #F7FAFF;
    color: #3C4A63; font-size: 12px; font-weight: 600; cursor: pointer; }
.fin-otype--on { border-color: #1E88FF; background: #1E88FF; color: #fff; }

.fin-chips { display: flex; flex-wrap: wrap; gap: 5px; }
.fin-chip { padding: 5px 10px; border-radius: 999px; border: 1px solid #DCE5F2; background: #fff;
    color: #3C4A63; font-size: 11px; cursor: pointer; }
.fin-chip--on { border-color: #1E88FF; background: rgba(30, 136, 255, 0.1); color: #0568FF; font-weight: 600; }

.fin-params { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 8px; }
.fin-param { display: flex; flex-direction: column; gap: 3px; }
.fin-param__name { font-size: 10.5px; line-height: 1.25; color: #4C586A; }
.fin-param__unit { color: #96A3B6; font-style: normal; }
.fin-input { width: 100%; box-sizing: border-box; padding: 6px 8px; border: 1px solid #DCE5F2;
    border-radius: 8px; font-size: 12px; color: #0B1626; background: #fff; }
.fin-input--search { margin-bottom: 8px; }
.fin-input--qty { width: 62px; flex-shrink: 0; }

.fin-picker { list-style: none; margin: 0 0 8px; padding: 0; max-height: 210px; overflow-y: auto;
    border: 1px solid #EDF1F7; border-radius: 10px; }
.fin-pick { display: grid; grid-template-columns: 1fr auto auto; gap: 8px; align-items: baseline;
    width: 100%; padding: 7px 10px; border: 0; background: none; text-align: left; cursor: pointer; }
.fin-pick:hover { background: #F4F8FF; }
.fin-pick__name { font-size: 12px; color: #0B1626; }
.fin-pick__type { font-size: 9.5px; color: #96A3B6; }
.fin-pick__price { font-size: 11px; font-weight: 600; color: #0568FF; white-space: nowrap; }

.fin-lines { display: grid; gap: 6px; margin-bottom: 10px; }
.fin-line { display: flex; align-items: center; gap: 8px; padding: 6px 8px; border: 1px solid #EDF1F7;
    border-radius: 9px; }
.fin-line__name { flex: 1; font-size: 12px; color: #0B1626; }
.fin-line__price { display: block; font-size: 10px; color: #96A3B6; font-style: normal; }
.fin-line__drop { border: 0; background: none; color: #96A3B6; font-size: 16px; line-height: 1;
    cursor: pointer; padding: 0 4px; }
.fin-line__drop:hover { color: #D94A4A; }
.fin-sum { margin: 2px 0 0; font-size: 11.5px; color: #3C4A63; }

.fin-horizon { display: grid; gap: 4px; margin: 12px 0 10px; font-size: 11.5px; color: #3C4A63; }
.fin-horizon input { width: 100%; }

.fin-btn { display: inline-flex; align-items: center; gap: 7px; height: 40px; padding: 0 18px;
    border: 0; border-radius: 11px; background: var(--accent, #1E88FF); color: #fff; font-weight: 700;
    font-size: 13px; cursor: pointer; text-decoration: none; }
.fin-btn:disabled { opacity: 0.6; cursor: progress; }
.fin-btn--ghost { background: transparent; color: #0568FF; border: 1px solid #1E88FF; }
.fin-btn--wide { width: 100%; justify-content: center; }

.fin-note { margin: 10px 0 0; font-size: 11px; color: #4C586A; line-height: 1.45; }
.fin-note--bad { padding: 9px 11px; border-radius: 9px; background: rgba(217, 74, 74, 0.08); color: #B42318; }
.fin-problem { display: block; margin-top: 3px; }
.fin-note__item { margin-left: 8px; }

.fin-empty { margin: 0; padding: 40px 10px; text-align: center; font-size: 12.5px; line-height: 1.5;
    color: #4C586A; }

.fin-tco, .fin-years { width: 100%; border-collapse: collapse; font-size: 11.5px; }
.fin-tco th, .fin-tco td, .fin-years th, .fin-years td { padding: 7px 6px; text-align: right;
    border-bottom: 1px solid #EDF1F7; }
.fin-tco thead th, .fin-years thead th { font-size: 10px; font-weight: 600; color: #607089; }
.fin-tco tbody th, .fin-years tbody th { text-align: left; font-weight: 600; color: #0B1626; }
.fin-tco__total { font-weight: 700; }
.fin-tco__hint { display: block; font-size: 9.5px; font-weight: 400; color: #96A3B6; font-style: normal; }
.fin-best { background: rgba(30, 136, 255, 0.07); }
.fin-badge { display: inline-block; margin-top: 2px; padding: 1px 6px; border-radius: 999px;
    background: #1E88FF; color: #fff; font-size: 9px; font-weight: 700; }

.fin-split { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.fin-money { list-style: none; margin: 0; padding: 0; font-size: 11.5px; }
.fin-money li { display: flex; justify-content: space-between; gap: 10px; padding: 4px 0;
    border-bottom: 1px dashed #EDF1F7; color: #3C4A63; }
.fin-money--total { border-bottom: 0 !important; margin-top: 3px; padding-top: 6px !important;
    border-top: 2px solid #DCE5F2; color: #0B1626; }

.fin-kpi { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 8px; }
.fin-kpi__cell { padding: 9px 11px; border: 1px solid #EDF1F7; border-radius: 10px; background: #FAFCFF; }
.fin-kpi__cell span { display: block; font-size: 10px; color: #607089; margin-bottom: 2px; }
.fin-kpi__cell b { font-size: 13.5px; color: #0B1626; }
.fin-neg { color: #B42318; }

.fin-sens { margin-bottom: 12px; }
.fin-sens__head { display: flex; justify-content: space-between; align-items: baseline; font-size: 11.5px;
    font-weight: 600; color: #0B1626; margin-bottom: 5px; }
.fin-sens__head i { font-size: 10px; font-weight: 400; color: #96A3B6; font-style: normal; }
.fin-sens__bars { display: grid; grid-template-columns: repeat(5, 1fr); gap: 6px; }
.fin-sens__point { display: grid; gap: 3px; justify-items: center; font-size: 9.5px; color: #607089; }
/* Полоса разделена пополам: верхняя половина растёт от базовой линии вверх,
   нижняя — вниз. Базовая линия проходит по центру и всегда на месте,
   поэтому видно, в какую сторону уводит допущение. */
.fin-sens__bar { width: 100%; height: 72px; display: flex; flex-direction: column; justify-content: center;
    background: #F7FAFF; border-radius: 6px; overflow: hidden; }
.fin-sens__bar i { display: block; width: 100%; }
.fin-sens__up { background: #1E88FF; order: 1; }
.fin-sens__down { background: #F0948B; order: 2; }
.fin-sens__bar i:first-child { border-radius: 0 0 6px 6px; }
.fin-sens__bar i:last-child { border-radius: 6px 6px 0 0; }
.fin-sens__value { white-space: nowrap; }

.fin-warn { margin: 0; padding-left: 18px; font-size: 11px; line-height: 1.5; color: #4C586A; }
.fin-warn li { margin-bottom: 3px; }

.fin-scheme-mini--on { border: 1px solid rgba(30, 136, 255, 0.35); border-radius: 12px; }
.fin-scheme-mini__img { position: relative; height: 84px; margin-bottom: 6px; }
.fin-scheme-mini__img img { position: absolute; height: 100%; width: 100%; inset: 0; object-fit: contain;
    mix-blend-mode: multiply; }
.fin-scheme-mini__flag { display: inline-block; padding: 1px 7px; border-radius: 999px;
    background: rgba(30, 136, 255, 0.12); color: #0568FF; font-size: 9px; font-weight: 700; }

.fin-cmp-table { width: 100%; border-collapse: collapse; font-size: 11px; }
.fin-cmp-table th, .fin-cmp-table td { padding: 7px 5px; text-align: center; }
.fin-cmp-table thead th { font-size: 10.5px; font-weight: 700; color: #142033; }
.fin-cmp-table tbody th { text-align: left; font-weight: 500; color: #142033; }
.fin-cmp-table tbody tr { border-top: 1px solid rgba(36, 83, 151, 0.1); }
.fin-yes { color: #15813D; font-weight: 700; }
.fin-no { color: #D94A4A; font-weight: 700; }
.fin-cmp__sub { display: block; font-size: 8.5px; font-weight: 500; color: #607089; }

@media (max-width: 1000px) {
    .fin-grid { grid-template-columns: 1fr; }
}
</style>
