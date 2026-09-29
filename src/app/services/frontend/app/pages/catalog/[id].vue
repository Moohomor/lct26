<script setup lang="ts">
useHead({ title: 'Карточка решения' })

// Страница решения из /api/v1/catalog/{id}. Раньше в каталоге стояла
// ссылка «#», поэтому посмотреть ТТХ и цену позиции было негде, хотя
// бэкенд отдаёт 52 поля.
//
// Лежит рядом с index.vue, а не как pages/catalog.vue: одноимённый файл
// Nuxt делает родителем вложенных страниц и требует от него <NuxtPage />.
// Без него переход на /catalog/<id> давал пустую страницу — компонент не
// монтировался, запрос к бэкенду не уходил, полоса загрузки висела.
const route = useRoute()
const id = computed(() => String(route.params.id ?? ''))

const { $fetchApi } = useNuxtApp()
const apiBase = useRuntimeConfig().public.apiBase.replace(/\/$/, '')

const STATUS_LABEL: Record<string, string> = {
  operation: 'В эксплуатации',
  piloting: 'Пилот',
  rnd: 'НИОКР',
}

const { data: raw, error, pending } = await useAsyncData(
  'solution',
  () => $fetchApi(`/api/v1/catalog/${id.value}`),
  { watch: [id] },
)

// В шаблон отдаются готовые поля, а не ref с приведением типа: каст
// (item as any) в разметке лишний раз касается распаковки ref.
type Solution = Record<string, any>

const item = computed<Solution | null>(() => (raw.value as Solution) ?? null)
const photo = computed(() => {
  const url = item.value?.photo_url
  if (!url) return null
  return url.startsWith('http') ? url : `${apiBase}${url}`
})
const tags = computed(() => {
  const s = item.value
  if (!s) return []
  const out: Array<{ text: string; cls?: string }> = []
  if (s.solution_type?.name) out.push({ text: s.solution_type.name })
  if (s.industry) out.push({ text: s.industry })
  if (s.region) out.push({ text: s.region })
  if (s.status) {
    out.push({ text: STATUS_LABEL[s.status] ?? s.status, cls: 'rpd-tag--status' })
  }
  if (s.trl) out.push({ text: `УГТ ${s.trl} из 9` })
  return out
})

const money = (v: number | null | undefined) =>
  v === null || v === undefined
    ? null
    : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(v) + ' ₽'
const num = (v: number | null | undefined, digits = 1) =>
  v === null || v === undefined
    ? null
    : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: digits }).format(v)

const specs = computed(() => {
  const s = item.value
  if (!s) return []
  const rows: Array<[string, string | null]> = [
    ['Грузоподъёмность', s.payload_kg ? num(s.payload_kg, 0) + ' кг' : null],
    ['Масса', s.own_weight_kg ? num(s.own_weight_kg, 0) + ' кг' : null],
    ['Длина', s.length_m ? num(s.length_m, 2) + ' м' : null],
    ['Ширина', s.width_m ? num(s.width_m, 2) + ' м' : null],
    ['Высота', s.height_m ? num(s.height_m, 2) + ' м' : null],
    ['Мин. проезд', s.min_passage_width_m ? num(s.min_passage_width_m, 2) + ' м' : null],
    ['Высота подъёма', s.lift_height_m ? num(s.lift_height_m, 2) + ' м' : null],
    ['Скорость', s.max_speed_mps ? num(s.max_speed_mps, 2) + ' м/с' : null],
    [
      'Производительность',
      s.throughput_per_hour ? num(s.throughput_per_hour, 0) + ' ' + (s.throughput_unit ?? '') : null,
    ],
    ['Автономность', s.autonomy_hours ? num(s.autonomy_hours, 0) + ' ч' : null],
    ['Зарядка', s.charge_time_min ? num(s.charge_time_min, 0) + ' мин' : null],
    [
      'Точность позиционирования',
      s.positioning_accuracy_mm ? num(s.positioning_accuracy_mm, 0) + ' мм' : null,
    ],
    ['Ёмкость АКБ', s.battery_capacity_kwh ? num(s.battery_capacity_kwh, 1) + ' кВт·ч' : null],
    ['Мощность зарядки', s.charge_power_kw ? num(s.charge_power_kw, 1) + ' кВт' : null],
    ['Ресурс АКБ', s.battery_lifetime_years ? num(s.battery_lifetime_years, 0) + ' лет' : null],
    ['Срок службы', s.lifetime_years ? num(s.lifetime_years, 0) + ' лет' : null],
    ['Мин. температура', s.min_temp_c != null ? num(s.min_temp_c, 0) + ' °C' : null],
    ['Макс. температура', s.max_temp_c != null ? num(s.max_temp_c, 0) + ' °C' : null],
    ['Шум', s.max_noise_dba != null ? num(s.max_noise_dba, 0) + ' дБА' : null],
    [
      'Навигация',
      Array.isArray(s.navigation_types) && s.navigation_types.length
        ? s.navigation_types.join(', ')
        : null,
    ],
  ]
  return rows.filter((r) => r[1] !== null).map(([label, value]) => ({ label, value: value as string }))
})

const priceRows = computed(() => {
  const s = item.value
  if (!s) return []
  return [
    { label: 'Оборудование', value: money(s.unit_price_rub) },
    { label: 'Программное обеспечение', value: money(s.software_price_rub) },
    { label: 'Внедрение', value: money(s.implementation_price_rub) },
    { label: 'Инфраструктура', value: money(s.infrastructure_price_rub) },
    {
      label: 'Сервис, % в год',
      value: s.service_rate_pct != null ? num(s.service_rate_pct, 1) + ' %' : null,
    },
  ].filter((r) => r.value)
})

const objectTypes = computed<Array<string>>(() => {
  const v = item.value?.applicable_object_types
  return Array.isArray(v) ? v : []
})

// applicable_object_types хранит коды (warehouse, airport), а читать их
// пользователю неудобно: подставляем названия из справочника. Если кода в
// справочнике нет, оставляем как есть — так видно, что данных не хватило,
// вместо молчаливого пропуска.
const objectTypeNames = useState<Record<string, string>>('object-type-names', () => ({}))
onMounted(async () => {
  if (Object.keys(objectTypeNames.value).length) return
  try {
    const list = await $fetchApi<any>('/api/v1/object-types')
    const items = Array.isArray(list) ? list : (list?.items ?? [])
    const map: Record<string, string> = {}
    for (const o of items) if (o?.code) map[o.code] = o.name ?? o.code
    objectTypeNames.value = map
  } catch {
    // Справочник недоступен — покажем коды, это лучше, чем ничего.
  }
})
const objectTypeLabels = computed(() =>
  objectTypes.value.map((code) => objectTypeNames.value[code] ?? code),
)

// Комплектации одной позиции. В списке каталога варианты скрыты, иначе
// одна и та же техника занимала бы несколько строк подряд, — поэтому
// различия видны только здесь.
const variants = computed(() => {
  const list = item.value?.variants
  if (!Array.isArray(list)) return []
  return list.map((v: any) => ({
    id: v.id,
    name: v.name,
    label: v.variant_label || null,
    price: money(v.unit_price_rub),
  }))
})
const completeness = computed(() =>
  item.value?.completeness != null ? num(item.value.completeness, 0) + '%' : null,
)
const price = computed(() => money(item.value?.unit_price_rub) ?? 'Цена по запросу')
</script>

<template>
    <div>
        <div class="rpd-root">
            <div class="rpd-shell">
                <nav class="rpd-crumbs">
                    <NuxtLink to="/catalog">Каталог роботов</NuxtLink>
                    <span v-if="item"> / {{ item.name }}</span>
                </nav>

                <div v-if="pending" class="rpd-state">Загружаем карточку…</div>

                <div v-else-if="error || !item" class="rpd-state">
                    <p>Не удалось загрузить решение.</p>
                    <NuxtLink class="rpd-btn" to="/catalog">Вернуться в каталог</NuxtLink>
                </div>

                <template v-else>
                    <header class="rpd-head">
                        <div class="rpd-visual">
                            <img v-if="photo" :src="photo" :alt="item.name">
                            <div v-else class="rpd-visual--none">Нет фото</div>
                        </div>

                        <div class="rpd-title">
                            <h1>{{ item.name }}</h1>
                            <p class="rpd-maker">
                                {{ item.vendor?.name ?? 'Производитель не указан' }}
                                <span v-if="item.vendor?.country"> · {{ item.vendor.country }}</span>
                            </p>
                            <div class="rpd-tags">
                                <span v-for="t in tags" :key="t.text" class="rpd-tag" :class="t.cls">{{ t.text }}</span>
                            </div>
                            <p v-if="item.purpose" class="rpd-purpose">{{ item.purpose }}</p>
                            <p v-if="item.description" class="rpd-desc">{{ item.description }}</p>
                        </div>

                        <div class="rpd-price">
                            <div class="rpd-price__main">{{ price }}</div>
                            <div v-if="item.data_source" class="rpd-price__src">
                                Источник: {{ item.data_source.name }}
                            </div>
                            <div v-if="completeness" class="rpd-price__comp">Заполнено ТТХ: {{ completeness }}</div>
                        </div>
                    </header>

                    <section v-if="specs.length" class="rpd-block">
                        <h2>Технические характеристики</h2>
                        <dl class="rpd-specs">
                            <div v-for="s in specs" :key="s.label" class="rpd-spec">
                                <dt>{{ s.label }}</dt>
                                <dd>{{ s.value }}</dd>
                            </div>
                        </dl>
                    </section>

                    <section v-if="priceRows.length > 1" class="rpd-block">
                        <h2>Стоимость владения</h2>
                        <dl class="rpd-specs">
                            <div v-for="r in priceRows" :key="r.label" class="rpd-spec">
                                <dt>{{ r.label }}</dt>
                                <dd>{{ r.value }}</dd>
                            </div>
                        </dl>
                    </section>

                    <section v-if="variants.length" class="rpd-block">
                        <h2>Комплектации</h2>
                        <ul class="rpd-variants">
                            <li v-for="v in variants" :key="v.id" class="rpd-variant">
                                <span class="rpd-variant__name">
                                    {{ v.name }}
                                    <b v-if="v.label">{{ v.label }}</b>
                                </span>
                                <span class="rpd-variant__price">{{ v.price ?? 'Цена по запросу' }}</span>
                            </li>
                        </ul>
                    </section>

                    <section v-if="objectTypes.length || item.infrastructure_requirements" class="rpd-block">
                        <h2>Условия применения</h2>
                        <p v-if="objectTypeLabels.length">
                            Подходит для объектов: <b>{{ objectTypeLabels.join(', ') }}</b>
                        </p>
                        <p v-if="item.infrastructure_requirements">{{ item.infrastructure_requirements }}</p>
                    </section>
                </template>
            </div>
        </div>
    </div>
</template>

<style scoped>
.rpd-root { min-height: 100vh; padding: 18px 0 40px; font-family: 'Manrope', 'Inter', system-ui, sans-serif; color: #111A31; }
.rpd-shell { width: min(1180px, calc(100% - 24px)); margin: 0 auto; }

.rpd-crumbs { font-size: 13px; color: #6B7A93; margin-bottom: 14px; }
.rpd-crumbs a { color: #0568FF; text-decoration: none; }

.rpd-head { display: grid; grid-template-columns: 320px 1fr 240px; gap: 22px; align-items: start; }
.rpd-visual { background: #fff; border: 1px solid #E6ECF5; border-radius: 14px; padding: 12px; }
.rpd-visual img { width: 100%; height: 220px; object-fit: contain; }
.rpd-visual--none { height: 220px; display: grid; place-items: center; color: #9AA8BD; font-size: 13px; }

.rpd-title h1 { margin: 0 0 6px; font-size: 26px; }
.rpd-maker { margin: 0 0 10px; color: #6B7A93; font-size: 14px; }
.rpd-tags { display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }
.rpd-tag { font-size: 12px; padding: 3px 9px; border: 1px solid #DCE5F2; border-radius: 999px; color: #3C4A63; background: #F7FAFF; }
.rpd-tag--status { border-color: #9BE0B8; color: #067647; background: #ECFDF3; }
.rpd-purpose { margin: 0 0 6px; font-weight: 600; }
.rpd-desc { margin: 0; color: #3C4A63; line-height: 1.5; }

.rpd-price { background: #fff; border: 1px solid #E6ECF5; border-radius: 14px; padding: 16px; }
.rpd-price__main { font-size: 20px; font-weight: 700; color: #0568FF; }
.rpd-price__src, .rpd-price__comp { font-size: 12px; color: #6B7A93; margin-top: 6px; }

.rpd-block { margin-top: 24px; background: #fff; border: 1px solid #E6ECF5; border-radius: 14px; padding: 18px; }
.rpd-block h2 { margin: 0 0 14px; font-size: 18px; }
.rpd-specs { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 10px 20px; margin: 0; }
.rpd-spec { display: flex; justify-content: space-between; gap: 12px; border-bottom: 1px dashed #EDF1F7; padding-bottom: 6px; }
.rpd-spec dt { color: #6B7A93; font-size: 13px; }
.rpd-spec dd { margin: 0; font-size: 13px; font-weight: 600; }

.rpd-variants { list-style: none; margin: 0; padding: 0; }
.rpd-variant { display: flex; justify-content: space-between; gap: 14px; align-items: baseline;
  border-bottom: 1px dashed #EDF1F7; padding-bottom: 6px; margin-bottom: 6px; font-size: 13px; }
.rpd-variant:last-child { border-bottom: 0; margin-bottom: 0; }
.rpd-variant__name b { margin-left: 6px; color: #0568FF; font-weight: 600; }
.rpd-variant__price { white-space: nowrap; font-weight: 600; }

.rpd-state { padding: 48px 20px; text-align: center; color: #6B7A93; }
.rpd-btn { display: inline-block; margin-top: 10px; padding: 8px 14px; background: #0568FF; color: #fff; border-radius: 8px; text-decoration: none; }

@media (max-width: 900px) {
  .rpd-head { grid-template-columns: 1fr; }
}
</style>
