"""Нормативы расчётной модели: CAPEX, OPEX, амортизация, RaaS, чувствительность.

Ни один коэффициент не «зашит» в код экономики — он читается из таблицы
`normatives`. У каждого значения обязательно есть источник: листы «Легенда»
демо-датасета организатора, разделы «Дополнений для участников» либо прямое
допущение, помеченное как оценка.

Структура CAPEX/OPEX взята из листа «Легенда»:
    CAPEX = оборудование + ПО + интеграция + ПНР + обучение + резерв 10 %
    OPEX  = сервис + лицензии + энергия + расходники + замена АКБ (раз в 3–5 лет)
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

ORGANIZER_LEGEND = "Демо-датасет организатора, лист «Легенда»"
ORGANIZER_SUPPLEMENTS = "«Дополнения для участников», организатор хакатона"
ESTIMATE = "Оценочное допущение платформы (уточняется запросом КП)"


@dataclass(frozen=True)
class NormativeDef:
    code: str
    name: str
    value: Decimal
    unit: str | None
    category: str
    source: str
    note: str | None = None
    is_editable: bool = True


def _d(value: str) -> Decimal:
    return Decimal(value)


NORMATIVES: tuple[NormativeDef, ...] = (
    # ── Общие ─────────────────────────────────────────────────────────────
    NormativeDef(
        "calc.horizon_years", "Горизонт расчёта по умолчанию", _d("5"), "лет",
        "общие", ORGANIZER_SUPPLEMENTS,
        "Минимальный горизонт по ТЗ — 5 лет; TCO считается на этом горизонте.",
    ),
    NormativeDef(
        "calc.vat_rate", "Ставка НДС", _d("20"), "%",
        "общие", ORGANIZER_SUPPLEMENTS,
        "Цены каталога организатора указаны с НДС, поэтому НДС добавляется "
        "только к позициям, цена которых дана без НДС.",
    ),
    NormativeDef(
        "payroll.multiplier", "Коэффициент начислений на ФОТ", _d("1.302"), "×",
        "персонал", ORGANIZER_LEGEND,
        "Зарплата указана gross; начисления добавляются этим коэффициентом.",
    ),

    # ── CAPEX ─────────────────────────────────────────────────────────────
    NormativeDef(
        "capex.software_pct", "Доля ПО в CAPEX", _d("8"), "% от CAPEX оборудования",
        "капитальные", ESTIMATE,
        "Управляющее и интеграционное ПО, лицензии на единицу техники.",
    ),
    NormativeDef(
        "capex.integration_pct", "Доля интеграции в CAPEX", _d("12"), "% от CAPEX оборудования",
        "капитальные", ESTIMATE,
        "Сопряжение с WMS/МИС/ЛИС, настройка маршрутов и безопасности.",
    ),
    NormativeDef(
        "capex.commissioning_pct", "Доля ПНР в CAPEX", _d("7"), "% от CAPEX оборудования",
        "капитальные", ESTIMATE,
        "Пусконаладка, приёмка, обучение персонала.",
    ),
    NormativeDef(
        "capex.training_pct", "Доля обучения в CAPEX", _d("3"), "% от CAPEX оборудования",
        "капитальные", ESTIMATE,
        "Обучение операторов и обслуживающего персонала.",
    ),
    NormativeDef(
        "capex.reserve_pct", "Резерв CAPEX", _d("10"), "%",
        "капитальные", ORGANIZER_LEGEND,
        "Резерв на непредвиденные работы по листу «Легенда».",
    ),
    NormativeDef(
        "capex.charging_station_rub", "Стоимость зарядной станции", _d("350000"), "руб./станция",
        "капитальные", ESTIMATE,
        "Одна станция обслуживает в среднем 2–3 робота; при RaaS входит в платёж.",
    ),
    NormativeDef(
        "capex.battery_replacement_rub_per_kwh", "Стоимость замены АКБ", _d("12000"), "руб./кВт·ч",
        "капитальные", ESTIMATE,
        "Замена аккумуляторной батареи при исчерпании ресурса.",
    ),
    NormativeDef(
        "capex.solution_lifetime_years", "Срок службы оборудования", _d("7"), "лет",
        "капитальные", ESTIMATE,
        "Средний срок службы мобильной робототехники до капитального ремонта.",
    ),
    NormativeDef(
        "capex.battery_lifetime_years", "Ресурс АКБ", _d("4"), "лет",
        "капитальные", ORGANIZER_LEGEND,
        "Замена АКБ раз в 3–5 лет по «Дополнениям»; принято 4 года.",
    ),
    NormativeDef(
        "capex.amortization_years", "Срок амортизации", _d("5"), "лет",
        "капитальные", ORGANIZER_SUPPLEMENTS,
        "Амортизация включается в годовой эффект линейно (ТЗ 3.5.4).",
    ),

    # ── OPEX ──────────────────────────────────────────────────────────────
    NormativeDef(
        "opex.service_pct", "Годовой сервис оборудования", _d("10"), "% от цены изделия в год",
        "эксплуатационные", ESTIMATE,
        "Если у решения задан свой service_rate_pct, он приоритетнее.",
    ),
    NormativeDef(
        "opex.license_pct", "Годовые лицензии ПО", _d("12"), "% от стоимости ПО в год",
        "эксплуатационные", ESTIMATE,
    ),
    NormativeDef(
        "opex.energy_rub_per_kwh", "Стоимость электроэнергии", _d("7.5"), "руб./кВт·ч",
        "эксплуатационные", ESTIMATE,
        "Тариф для промышленных потребителей; в аэропорту и медицине выше.",
    ),
    NormativeDef(
        "opex.consumables_pct", "Расходные материалы", _d("3"), "% от CAPEX в год",
        "эксплуатационные", ORGANIZER_LEGEND,
        "Щётки, аккумуляторные модули, спрей и т. п.",
    ),
    NormativeDef(
        "opex.integration_support_pct", "Сопровождение интеграции", _d("6"), "% от CAPEX в год",
        "эксплуатационные", ESTIMATE,
        "Доработка и поддержка интеграции с информационными системами.",
    ),
    NormativeDef(
        "opex.insurance_pct", "Страхование имущества", _d("1.5"), "% от CAPEX в год",
        "эксплуатационные", ESTIMATE,
    ),

    # ── Производительность и sizing ────────────────────────────────────────
    NormativeDef(
        "sizing.availability", "Коэффициент технической готовности", _d("0.95"), "×",
        "расчёт", ESTIMATE,
        "Плановое ТО, замены, ожидание зарядки.",
    ),
    NormativeDef(
        "sizing.load_factor", "Коэффициент использования", _d("0.80"), "×",
        "расчёт", ORGANIZER_LEGEND,
        "Диапазон AMR по «Дополнениям» — 70–85 %, принято 80 %.",
    ),
    NormativeDef(
        "sizing.availability_low", "Коэффициент готовности, нижняя граница", _d("0.90"), "×",
        "расчёт", ORGANIZER_LEGEND,
        "Резерв мощности 15–20 % по «Дополнениям» — диапазон 0,80–0,85 готовности.",
    ),
    NormativeDef(
        "sizing.availability_high", "Коэффициент готовности, верхняя граница", _d("0.95"), "×",
        "расчёт", ORGANIZER_LEGEND,
    ),
    NormativeDef(
        "sizing.passage_margin_m", "Запас на ширину проезда", _d("0.3"), "м",
        "расчёт", ESTIMATE,
        "Дополнительно к ширине корпуса: разминовка, безопасность, погрешность.",
    ),

    # ── Экономика эффекта ─────────────────────────────────────────────────
    NormativeDef(
        "effect.headcount_fte_per_robot", "Замещаемый сотрудник на 1 AMR", _d("1.0"), "FTE",
        "эффект", ESTIMATE,
        "Один робот стабильно замещает одну ставку в пиковые часы.",
    ),
    NormativeDef(
        "effect.picker_hourly_workload", "Годовая выработка сотрудника", _d("1970"), "ч/год",
        "эффект", ORGANIZER_LEGEND,
        "365 дней × 2 смены × 11 ч × коэффициент 0,25 потерь рабочего времени.",
    ),
    NormativeDef(
        "effect.safety_incident_avoidance_rub", "Эффект от снижения травматизма", _d("0"), "руб./год",
        "эффект", ESTIMATE,
        "По умолчанию не учитывается: включается только при явном допущении сценария.",
    ),
    NormativeDef(
        "effect.quality_loss_pct", "Снижение потерь от ошибок и повреждений", _d("0"), "%",
        "эффект", ESTIMATE,
        "По умолчанию 0: включается сценарием при наличии обоснования.",
    ),
    NormativeDef(
        "effect.throughput_uplift_pct", "Прирост пропускной способности", _d("0"), "%",
        "эффект", ESTIMATE,
        "Учитывается только если решение реально разгружает узкое место.",
    ),
    NormativeDef(
        "effect.overtime_premium_pct", "Надбавка за сверхурочные", _d("0.5"), "%",
        "эффект", ESTIMATE,
        "Экономия на сверхурочных в пиковые периоды.",
    ),

    # ── RaaS / лизинг ─────────────────────────────────────────────────────
    NormativeDef(
        "raas.term_months", "Срок договора RaaS по умолчанию", _d("36"), "мес.",
        "raas", ORGANIZER_SUPPLEMENTS,
        "Типовой горизонт сервисной модели из «Дополнений».",
    ),
    NormativeDef(
        "raas.rate_pct_of_capex_per_year", "Ставка RaaS", _d("28"), "% от CAPEX в год",
        "raas", ORGANIZER_SUPPLEMENTS,
        "Включает сервис, ПО, замену АКБ и гарантию доступности; ТЗ 3.5.5.",
    ),
    NormativeDef(
        "raas.min_availability", "Гарантированная доступность по договору", _d("0.97"), "×",
        "raas", ORGANIZER_SUPPLEMENTS,
        "Штраф за недостижение уровня доступности закладывается в цену договора.",
    ),
    NormativeDef(
        "raas.setup_pct", "Плата за ввод в эксплуатацию", _d("8"), "% от CAPEX",
        "raas", ESTIMATE,
        "Разовый платёж при старте RaaS-контракта.",
    ),
    NormativeDef(
        "raas.exit_pct", "Стоимость выхода из контракта", _d("15"), "% от CAPEX",
        "raas", ESTIMATE,
        "Демонтаж и вывоз оборудования при досрочном расторжении.",
    ),
    NormativeDef(
        "finance.discount_rate", "Ставка дисконтирования", _d("0.14"), "доля",
        "финансы", ESTIMATE,
        "Используется для NPV; простая окупаемость считается без дисконтирования.",
    ),
    NormativeDef(
        "finance.lease_rate_pct", "Ставка лизинга", _d("18"), "% годовых",
        "финансы", ESTIMATE,
    ),
    NormativeDef(
        "finance.lease_down_pct", "Аванс лизинга", _d("20"), "%",
        "финансы", ESTIMATE,
    ),

    # ── Энергетика ────────────────────────────────────────────────────────
    NormativeDef(
        "battery.amr_kwh", "Ёмкость АКБ AMR", _d("2.0"), "кВт·ч",
        "энергетика", ESTIMATE,
        "Типовая батарея мобильной платформы грузоподъёмностью до 1,5 т.",
    ),
    NormativeDef(
        "battery.fmr_kwh", "Ёмкость АКБ вилочного робота", _d("8.0"), "кВт·ч",
        "энергетика", ESTIMATE,
    ),
    NormativeDef(
        "battery.cleaner_kwh", "Ёмкость АКБ уборщика", _d("3.0"), "кВт·ч",
        "энергетика", ESTIMATE,
    ),
    NormativeDef(
        "battery.delivery_robot_kwh", "Ёмкость АКБ робота-доставщика", _d("1.5"), "кВт·ч",
        "энергетика", ESTIMATE,
    ),
    NormativeDef(
        "battery.asrs_kwh", "Ёмкость АКБ AS/RS и шаттла", _d("5.0"), "кВт·ч",
        "энергетика", ESTIMATE,
        "Батареи роботов-носителей внутри каналов хранения.",
    ),
    NormativeDef(
        "battery.tugger_kwh", "Ёмкость АКБ тягача", _d("20.0"), "кВт·ч",
        "энергетика", ESTIMATE,
        "Тягачи работают на топливе; значение — для расчёта замены АКБ "
        "вспомогательного оборудования.",
    ),
    NormativeDef(
        "battery.truck_kwh", "Ёмкость АКБ беспилотного грузовика", _d("36.0"), "кВт·ч",
        "энергетика", ESTIMATE,
        "Соответствует заявленной ёмкости EVOCARGO N1.",
    ),
    NormativeDef(
        "energy.cycles_per_year", "Циклов «работа + зарядка» в год", _d("8760"), "ч/год",
        "энергетика", ESTIMATE,
        "Знаменатель — год; фактическое число циклов = 8760 / (автономность + зарядка).",
    ),

    # ── Оценка цены при отсутствии данных ─────────────────────────────────
    NormativeDef(
        "pricing.default_amr_rub", "Оценка цены AMR при отсутствии данных", _d("2700000"), "руб.",
        "цены", ESTIMATE,
        "Ориентир по каталогу организатора (Ronavi H1500).",
    ),
    NormativeDef(
        "pricing.default_fmr_rub", "Оценка цены FMR при отсутствии данных", _d("4300000"), "руб.",
        "цены", ESTIMATE,
        "Ориентир по каталогу организатора (DMR Carrier P).",
    ),
    NormativeDef(
        "pricing.default_cleaner_rub", "Оценка цены уборщика при отсутствии данных", _d("1900000"), "руб.",
        "цены", ESTIMATE,
        "Ориентир по каталогу организатора (MARK 2 SE).",
    ),
    NormativeDef(
        "pricing.default_tugger_rub", "Оценка цены тягача при отсутствии данных", _d("3500000"), "руб.",
        "цены", ESTIMATE,
    ),
    NormativeDef(
        "pricing.default_delivery_robot_rub", "Оценка цены робота-доставщика", _d("1400000"), "руб.",
        "цены", ESTIMATE,
        "Ориентир по позиции Ronavi SD того же класса грузоподъёмности.",
    ),
    NormativeDef(
        "pricing.default_asrs_rub", "Оценка цены стационарной системы", _d("10000000"), "руб.",
        "цены", ESTIMATE,
        "Ориентир по позиции AS-RS P каталога организатора.",
    ),
    NormativeDef(
        "pricing.default_other_rub", "Оценка цены прочих решений", _d("2500000"), "руб.",
        "цены", ESTIMATE,
    ),

    # ── Чувствительность ──────────────────────────────────────────────────
    NormativeDef(
        "sensitivity.steps", "Число точек по оси чувствительности", _d("5"), "шт.",
        "чувствительность", ESTIMATE,
        "Значения параметра от −30 % до +30 % от базового.",
    ),
    NormativeDef(
        "sensitivity.range_pct", "Диапазон варьирования параметра", _d("30"), "%",
        "чувствительность", ESTIMATE,
        "ТЗ 3.5.9: отклонение не менее ±30 % от базового значения.",
    ),
)

# Параметры, по которым строится обязательный анализ чувствительности (ТЗ 3.5.9).
SENSITIVITY_PARAMS: tuple[tuple[str, str, str], ...] = (
    ("equipment_cost", "Стоимость оборудования", "unit_price_rub"),
    ("operations_volume", "Объём операций", "__operations__"),
    ("labor_cost", "Стоимость персонала", "__labor__"),
)

#: Допустимые границы коэффициента. Один и тот же словарь отвечает на два
#: вопроса: «можно ли администратору поставить такое значение» (ТЗ 3.5.8) и
#: «в каком диапазоне пользователь может переопределить допущение сценария».
#: Дублировать эти числа в двух местах означает рано или поздно разрешить
#: пользователю то, что админка считает опечаткой.
NORMATIVE_RANGES: dict[str, tuple[Decimal, Decimal]] = {
    "calc.horizon_years": (Decimal("1"), Decimal("15")),
    "calc.vat_rate": (Decimal("0"), Decimal("40")),
    "payroll.multiplier": (Decimal("1"), Decimal("2.5")),
    "capex.software_pct": (Decimal("0"), Decimal("40")),
    "capex.integration_pct": (Decimal("0"), Decimal("50")),
    "capex.commissioning_pct": (Decimal("0"), Decimal("30")),
    "capex.training_pct": (Decimal("0"), Decimal("20")),
    "capex.reserve_pct": (Decimal("0"), Decimal("30")),
    "capex.amortization_years": (Decimal("1"), Decimal("15")),
    "capex.solution_lifetime_years": (Decimal("1"), Decimal("20")),
    "capex.battery_lifetime_years": (Decimal("1"), Decimal("10")),
    "opex.service_pct": (Decimal("0"), Decimal("50")),
    "opex.software_license_pct": (Decimal("0"), Decimal("40")),
    "opex.energy_price_kwh": (Decimal("0"), Decimal("100")),
    "raas.rate_pct_of_capex_per_year": (Decimal("5"), Decimal("80")),
    "raas.term_months": (Decimal("1"), Decimal("120")),
    "finance.discount_rate": (Decimal("0"), Decimal("1")),
    "sizing.load_factor": (Decimal("0.3"), Decimal("1")),
    "sizing.availability": (Decimal("0.5"), Decimal("1")),
    "effect.headcount_fte_per_robot": (Decimal("0.1"), Decimal("10")),
    "effect.maintenance_pct_capex": (Decimal("0"), Decimal("30")),
    "labor.forklift_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.operator_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.warehouse_worker_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.picker_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.loader_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.driver_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.nurse_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.doctor_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.orderly_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.sanitary_salary_rub": (Decimal("10000"), Decimal("500000")),
    "labor.total_headcount": (Decimal("1"), Decimal("10000")),
}


#: Границы переопределения допущения в сценарии. По умолчанию совпадают с
#: диапазонами админки, и расходятся только там, где пользователь двигает не
#: сам коэффициент, а множитель к нему: анализ чувствительности по ТЗ 3.5.9
#: обязан отклонять параметр и вниз, и вверх, поэтому «зарплата × 0,7» —
#: законный результат расчёта, а «коэффициент начислений = 0,7» — опечатка,
#: которую администратору видно, и она отвергается.
SCENARIO_RANGES: dict[str, tuple[Decimal, Decimal]] = {
    **NORMATIVE_RANGES,
    "payroll.multiplier": (Decimal("0.5"), Decimal("2.5")),
}


def by_code() -> dict[str, NormativeDef]:
    return {n.code: n for n in NORMATIVES}
