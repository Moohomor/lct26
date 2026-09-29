<script setup lang="ts">
useHead({ title: 'Карточка решения' })

// Страница решения из /api/v1/catalog/{id}. Раньше в каталоге стояла
// ссылка «#», поэтому посмотреть ТТХ и цену позиции было негде, хотя
// бэкенд отдаёт 52 поля.
const route = useRoute()
const id = computed(() => String(route.params.id ?? ''))

const { $fetchApi } = useNuxtApp()
const apiBase = useRuntimeConfig().public.apiBase.replace(/\/$/, '')

const STATUS_LABEL: Record<string, string> = {
  operation: 'В эксплуатации',
  piloting: 'Пилот',
  rnd: 'НИОКР',
}

const { data: item, error, pending } = await useAsyncData(
  () => `solution-${id.value}`,
  () => $fetchApi(`/api/v1/catalog/${id.value}`),
)

const photo = computed(() => {
  const url = (item.value as { photo_url?: string | null } | null)?.photo_url
  if (!url) return null
  return url.startsWith('http') ? url : `${apiBase}${url}`
})

const money = (v: number | null | undefined) =>
  v === null || v === undefined
    ? null
    : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 0 }).format(v) + ' ₽'

const num = (v: number | null | undefined, digits = 1) =>
  v === null || v === undefined ? null : new Intl.NumberFormat('ru-RU', { maximumFractionDigits: digits }).format(v)

// ТТХ: подписи берём у модели, а не пишем здесь, чтобы переводчик
// правил одно место.
const SPEC_FIELDS: Array<[string, (v: any, s: any) => string | null]> = [
  ['payload_kg', (v) => (v ? num(v, 0) + ' кг' : null), 'Грузоподъёмность'],
  ['own_weight_kg', (v) => (v ? num(v, 0) + ' кг' : null), 'Масса'],
  ['length_m', (v) => (v ? num(v, 2) + ' м' : null), 'Длина'],
  ['width_m', (v) => (v ? num(v, 2) + ' м' : null), 'Ширина'],
  ['height_m', (v) => (v ? num(v, 2) + ' м' : null), 'Высота'],
  ['min_passage_width_m', (v) => (v ? num(v, 2) + ' м' : null), 'Мин. проезд'],
  ['lift_height_m', (v) => (v ? num(v, 2) + ' м' : null), 'Высота подъёма'],
  ['max_speed_mps', (v) => (v ? num(v, 2) + ' м/с' : null), 'Скорость'],
  ['throughput', (v, s) => (v ? num(v, 0) + ' ' + (s.throughput_unit ?? '') : null), 'Производительность'],
  ['autonomy_hours', (v) => (v ? num(v, 0) + ' ч' : null), 'Автономность'],
  ['charge_time_min', (v) => (v ? num(v, 0) + ' мин' : null), 'Зарядка'],
  ['positioning_accuracy_mm', (v) => (v ? num(v, 0) + ' мм' : null), 'Точность позиционирования'],
  ['battery_capacity_kwh', (v) => (v ? num(v, 1) + ' кВт·ч' : null), 'Ёмкость АКБ'],
  ['charge_power_kw', (v) => (v ? num(v, 1) + ' кВт' : null), 'Мощность зарядки'],
  ['battery_lifetime_years', (v) => (v ? num(v, 0) + ' лет' : null), 'Ресурс АКБ'],
  ['lifetime_years', (v) => (v ? num(v, 0) + ' лет' : null), 'Срок службы'],
  ['min_temp_c', (v) => (v ? num(v, 0) + ' °C' : null), 'Мин. температура'],
  ['max_temp_c', (v) => (v ? num(v, 0) + ' °C' : null), 'Макс. температура'],
  ['max_noise_dba', (v) => (v ? num(v, 0) + ' дБА' : null), 'Шум'],
  ['navigation_types', (v) => (Array.isArray(v) && v.length ? v.join(', ') : null), 'Навигация'],
]

const specs = computed(() => {
  const s = item.value as Record<string, any> | null
  if (!s) return []
  return SPEC_FIELDS.map(([key, fmt, label]) => {
    const raw = key === 'throughput' ? s.throughput_per_hour : s[key]
    return { label, value: raw != null ? fmt(raw, s) : null }
  }).filter((x) => x.value)
})

const priceRows = computed(() => {
  const s = item.value as Record<string, any> | null
  if (!s) return []
  return [
    { label: 'Оборудование', value: money(s.unit_price_rub) },
    { label: 'Программное обеспечение', value: money(s.software_price_rub) },
    { label: 'Внедрение', value: money(s.implementation_price_rub) },
    { label: 'Инфраструктура', value: money(s.infrastructure_price_rub) },
    { label: 'Сервис, % в год', value: s.service_rate_pct != null ? num(s.service_rate_pct, 1) + ' %' : null },
  ].filter((r) => r.value)
})

const objectTypes = computed(() => {
  const v = (item.value as Record<string, any> | null)?.applicable_object_types
  return Array.isArray(v) ? v : []
})
</script>

<template>
    <div>
        <div class="rpd-root">
            <div class="rpd-shell">
                <nav class="rpd-crumbs"><NuxtLink to="/catalog">Каталог роботов</NuxtLink> /
                    <span>{{ (item as any)?.name ?? 'Решение' }}</span></nav>

                <div v-if="pending" class="rpd-state">Загружаем карточку…</div>

                <div v-else-if="error || !item" class="rpd-state">
                    <p>Не удалось загрузить решение.</p>
                    <NuxtLink class="rpd-btn" to="/catalog">Вернуться в каталог</NuxtLink>
                </div>

                <template v-else>
                    <header class="rpd-head">
                        <div class="rpd-visual">
                            <img v-if="photo" :src="photo" :alt="(item as any).name">
                            <div v-else class="rpd-visual--none">Нет фото</div>
                        </div>
                        <div class="rpd-title">
                            <h1>{{ (item as any).name }}</h1>
                            <p class="rpd-maker">{{ (item as any).vendor?.name ?? 'Производитель не указан' }}<span
                                    v-if="(item as any).vendor?.country"> · {{ (item as any).vendor.country }}</span></p>
                            <div class="rpd-tags">
                                <span class="rpd-tag" v-if="(item as any).solution_type">{{ (item as any).solution_type.name }}</span>
                                <span class="rpd-tag" v-if="(item as any).industry">{{ (item as any).industry }}</span>
                                <span class="rpd-tag" v-if="(item as any).region">{{ (item as any).region }}</span>
                                <span class="rpd-tag rpd-tag--status">{{ STATUS_LABEL[(item as any).status] ?? (item as any).status }}</span>
                                <span class="rpd-tag" v-if="(item as any).trl">УГТ {{ (item as any).trl }} из 9</span>
                            </div>
                            <p class="rpd-purpose" v-if="(item as any).purpose">{{ (item as any).purpose }}</p>
                            <p class="rpd-desc" v-if="(item as any).description">{{ (item as any).description }}</p>
                        </div>
                        <div class="rpd-price">
                            <div class="rpd-price__main">{{ money((item as any).unit_price_rub) ?? 'Цена по запросу' }}</div>
                            <div class="rpd-price__src" v-if="(item as any).data_source">Источник:
                                {{ (item as any).data_source.name }}</div>
                            <div class="rpd-price__comp" v-if="(item as any).completeness">
                                Заполнено ТТХ: {{ num((item as any).completeness, 0) }}%
                            </div>
                        </div>
                    </header>

                    <section class="rpd-block" v-if="specs.length">
                        <h2>Технические характеристики</h2>
                        <dl class="rpd-specs">
                            <div v-for="s in specs" :key="s.label" class="rpd-spec">
                                <dt>{{ s.label }}</dt>
                                <dd>{{ s.value }}</dd>
                            </div>
                        </dl>
                    </section>

                    <section class="rpd-block" v-if="priceRows.length > 1">
                        <h2>Стоимость владения</h2>
                        <dl class="rpd-specs">
                            <div v-for="r in priceRows" :key="r.label" class="rpd-spec">
                                <dt>{{ r.label }}</dt>
                                <dd>{{ r.value }}</dd>
                            </div>
                        </dl>
                    </section>

                    <section class="rpd-block" v-if="objectTypes.length || (item as any).infrastructure_requirements">
                        <h2>Условия применения</h2>
                        <p v-if="objectTypes.length">Подходит для объектов:
                            <b>{{ objectTypes.join(', ') }}</b>
                        </p>
                        <p v-if="(item as any).infrastructure_requirements">
                            {{ (item as any).infrastructure_requirements }}</p>
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

.rpd-state { padding: 48px 20px; text-align: center; color: #6B7A93; }
.rpd-btn { display: inline-block; margin-top: 10px; padding: 8px 14px; background: #0568FF; color: #fff; border-radius: 8px; text-decoration: none; }

@media (max-width: 900px) {
  .rpd-head { grid-template-columns: 1fr; }
}
</style>
