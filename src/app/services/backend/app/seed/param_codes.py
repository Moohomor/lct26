"""Коды параметров объекта: контракт между данными, подбором, экономикой и UI.

Демо-датасет организатора задаёт параметры по-русски. Чтобы движок подбора и
экономическая модель не зависели от формулировок, каждому параметру
присвоен стабильный код, а русские названия хранятся как алиасы.

Один код может иметь несколько алиасов: одинаковая по смыслу величина в разных
листах названа по-разному («Мощность электроснабжения (доступная)» на складе и
«Доступная мощность для зарядной инфраструктуры» в аэропорту).
"""

from __future__ import annotations

import re

# Тип значения: number | integer | percent | text | enum
HINT_INTEGER = "integer"
HINT_NUMBER = "number"
HINT_PERCENT = "percent"
HINT_TEXT = "text"
HINT_ENUM = "enum"

# ─────────────────────────────────────────────────────────────────────────────
# Параметры объекта: код → (алиасы, подсказка типа, обязательность)
# ─────────────────────────────────────────────────────────────────────────────
PARAM_CODES: dict[str, tuple[tuple[str, ...], str, bool]] = {
    # ── Общие для всех типов объектов ──────────────────────────────────────
    "total_area_m2": (
        ("Общая площадь склада", "Суммарная площадь терминала (ов)", "Общая площадь здания(й)"),
        HINT_NUMBER,
        True,
    ),
    "power_available_kw": (
        ("Мощность электроснабжения (доступная)", "Доступная мощность для зарядной инфраструктуры"),
        HINT_NUMBER,
        False,
    ),
    "capex_budget_mrub": (("Планируемый бюджет на роботизацию (CAPEX)",), HINT_NUMBER, False),
    "horizon_years": (("Горизонт расчёта окупаемости",), HINT_INTEGER, False),
    "payroll_multiplier": (
        ("Коэффициент начислений на ФОТ (страховые взносы)", "Коэффициент начислений на ФОТ"),
        HINT_NUMBER,
        True,
    ),
    "noise_limit_dba": (
        ("Ограничения по уровню шума (зона)", "Требования к уровню шума в палатах (ночное время)"),
        HINT_NUMBER,
        False,
    ),
    "min_temp_c": (
        ("Температура в неотапливаемых зонах (перрон, зима)",),
        HINT_NUMBER,
        False,
    ),
    "has_skud": (
        (
            "Наличие системы контроля доступа (СКУД)",
            "Наличие СКУД (контроль доступа по зонам)",
        ),
        HINT_TEXT,
        False,
    ),
    "floors_count": (
        ("Количество этажей (мезонинов)", "Количество этажей (основной корпус)"),
        HINT_INTEGER,
        False,
    ),

    # ── Склад ──────────────────────────────────────────────────────────────
    "active_area_m2": (("Площадь активной (роботизируемой) зоны",), HINT_NUMBER, True),
    "ceiling_height_m": (("Высота потолков в зоне хранения",), HINT_NUMBER, False),
    "main_aisle_width_m": (("Ширина главных проездов",), HINT_NUMBER, True),
    "work_aisle_width_m": (("Ширина рабочих проходов между стеллажами",), HINT_NUMBER, True),
    "floor_covering": (("Тип напольного покрытия",), HINT_ENUM, False),
    "floor_roughness_mm": (("Ровность пола (отклонение)",), HINT_NUMBER, False),
    "shifts_per_day": (("Количество рабочих смен в сутки",), HINT_INTEGER, True),
    "working_days_per_year": (("Рабочих дней в году",), HINT_INTEGER, False),
    "shift_hours": (("Продолжительность смены",), HINT_NUMBER, True),
    "peak_factor": (("Пиковый коэффициент нагрузки",), HINT_NUMBER, True),
    "inbound_pallets_day": (("Объём приёмки (поддоны/сутки)",), HINT_NUMBER, True),
    "outbound_pallets_day": (("Объём отгрузки (поддоны/сутки)",), HINT_NUMBER, True),
    "picking_lines_day": (("Объём отбора (строк/сутки, всего)",), HINT_NUMBER, True),
    "picking_units_day": (("Объём отбора (штук/сутки, всего)",), HINT_NUMBER, False),
    "piece_pick_share_pct": (("Доля мелкоштучного отбора (piece-pick)",), HINT_PERCENT, False),
    "sku_count": (("Количество SKU (активных)",), HINT_INTEGER, True),
    "a_class_share_pct": (("Доля SKU с быстрым оборотом (A-класс)",), HINT_PERCENT, False),
    "total_headcount": (("Общая численность персонала склада",), HINT_INTEGER, True),
    "pickers_headcount": (("Из них: отборщики (комплектовщики)",), HINT_INTEGER, True),
    "forklift_ops_headcount": (("Из них: операторы погрузчиков",), HINT_INTEGER, False),
    "packing_ops_headcount": (("Из них: операторы упаковочных линий",), HINT_INTEGER, False),
    "picker_salary_rub": (("Средняя з/п отборщика (gross)",), HINT_NUMBER, True),
    "forklift_salary_rub": (("Средняя з/п оператора погрузчика (gross)",), HINT_NUMBER, False),
    "picker_productivity_lines_hour": (("Средняя выработка отборщика (строк/ч)",), HINT_NUMBER, True),
    "absenteeism_pct": (
        ("Коэффициент потерь рабочего времени (отпуск, болезнь, текучесть)",),
        HINT_PERCENT,
        False,
    ),
    "pick_route_length_m": (("Средняя длина маршрута отборщика на 1 строку",), HINT_NUMBER, False),
    "conveyor_length_m": (("Протяжённость конвейерной/транспортной системы",), HINT_NUMBER, False),
    "racking_system": (("Тип стеллажной системы",), HINT_ENUM, False),
    "pallet_positions": (("Количество паллетомест",), HINT_INTEGER, False),
    "pallet_weight_kg": (("Средняя масса грузовой единицы (паллет)",), HINT_NUMBER, True),
    "item_weight_kg": (("Средняя масса штучной единицы (SKU)",), HINT_NUMBER, False),
    "pallet_dims_mm": (("Средние габариты паллеты (Д×Ш×В)",), HINT_TEXT, False),
    "item_dims_mm": (("Средние габариты штучной единицы (Д×Ш×В)",), HINT_TEXT, False),
    "oversized_share_pct": (("Доля негабаритных/нестандартных грузов",), HINT_PERCENT, False),
    "has_wms": (("Наличие WMS",), HINT_TEXT, False),
    "has_erp": (("Наличие ERP/1С",), HINT_TEXT, False),

    # ── Аэропорт ───────────────────────────────────────────────────────────
    "apron_area_m2": (("Площадь перрона и технических зон",), HINT_NUMBER, False),
    "terminals_count": (("Количество терминалов",), HINT_INTEGER, False),
    "gates_count": (("Количество выходов на посадку (гейтов)",), HINT_INTEGER, False),
    "runways_count": (("Количество взлётно-посадочных полос",), HINT_INTEGER, False),
    "passenger_flow_myear": (("Пассажиропоток (млн пассажиров/год)",), HINT_NUMBER, False),
    "passengers_day": (("Среднесуточное количество пассажиров",), HINT_NUMBER, True),
    "passengers_peak_hour": (("Пиковое количество пассажиров в час (PHF)",), HINT_NUMBER, True),
    "transfer_share_pct": (("Доля трансферных пассажиров",), HINT_PERCENT, False),
    "checkin_desks": (("Количество стоек регистрации",), HINT_INTEGER, False),
    "flights_day": (("Среднесуточное количество рейсов (взлёт+посадка)",), HINT_NUMBER, True),
    "flights_peak_hour": (("Пиковое количество рейсов в час",), HINT_NUMBER, True),
    "tat_min": (("Среднее время оборота воздушного судна (TAT)",), HINT_NUMBER, False),
    "gse_ops_per_flight": (
        ("Среднее количество операций наземного обслуживания на 1 рейс",),
        HINT_NUMBER,
        False,
    ),
    "baggage_units_day": (("Объём перемещения багажа (единиц/сутки)",), HINT_NUMBER, True),
    "baggage_weight_kg": (("Средняя масса единицы багажа",), HINT_NUMBER, True),
    "baggage_carousels": (("Количество стоек выдачи багажа (каруселей)",), HINT_INTEGER, False),
    "onboard_meals_day": (("Объём бортового питания (порций/сутки)",), HINT_NUMBER, False),
    "refueling_flights_day": (("Объём заправки воздушных судов (рейсов/сут)",), HINT_NUMBER, False),
    "internal_tug_runs_day": (
        ("Суточное количество рейсов внутренних грузовых тележек (внутри терминала)",),
        HINT_NUMBER,
        False,
    ),
    "cleaning_machines": (("Количество уборочных машин (терминал)",), HINT_INTEGER, False),
    "cleaning_area_m2": (("Площадь, убираемая роботизированной уборкой",), HINT_NUMBER, True),
    "waste_containers_day": (("Суточный объём вывоза мусора (контейнеров)",), HINT_NUMBER, False),
    "ramp_headcount": (("Численность персонала наземного обслуживания (рамп)",), HINT_INTEGER, True),
    "terminal_headcount": (
        ("Численность персонала внутри терминала (логистика, уборка)",),
        HINT_INTEGER,
        True,
    ),
    "ramp_salary_rub": (
        ("Средняя з/п сотрудника наземного обслуживания (gross)",),
        HINT_NUMBER,
        True,
    ),
    "cleaner_salary_rub": (("Средняя з/п уборщика терминала (gross)",), HINT_NUMBER, False),
    "turnover_pct": (
        ("Годовая текучесть (персонал терминала)", "Годовая текучесть (немедицинский персонал)"),
        HINT_PERCENT,
        False,
    ),
    "security_zones": (("Зонирование (количество режимных зон)",), HINT_INTEGER, False),
    "airside_cert_required": (
        ("Требования по сертификации оборудования для airside",),
        HINT_TEXT,
        False,
    ),
    "has_fids": (("Наличие FIDS/AODB системы",), HINT_TEXT, False),
    "has_bms": (("Наличие BMS (системы управления зданием)",), HINT_TEXT, False),

    # ── Медицинское учреждение ─────────────────────────────────────────────
    "facility_type": (("Тип медицинского учреждения",), HINT_ENUM, True),
    "elevators_count": (("Количество лифтов (грузовых/медицинских)",), HINT_INTEGER, False),
    "beds_count": (("Количество коек (стационар)",), HINT_INTEGER, True),
    "bed_occupancy_pct": (
        ("Коечный фонд в эксплуатации (средняя занятость)",),
        HINT_PERCENT,
        False,
    ),
    "operating_rooms": (("Количество операционных",), HINT_INTEGER, False),
    "outpatient_visits_day": (("Количество амбулаторных посещений в сутки",), HINT_NUMBER, False),
    "inpatient_mode": (("Режим работы стационара",), HINT_TEXT, False),
    "outpatient_mode": (("Режим работы амбулатории",), HINT_TEXT, False),
    "medical_shifts_day": (
        ("Количество смен медперсонала (уход за пациентами)",),
        HINT_INTEGER,
        False,
    ),
    "peak_hours": (("Пиковое время логистической нагрузки",), HINT_TEXT, False),
    "meals_per_day": (("Количество кормлений в сутки",), HINT_INTEGER, False),
    "meals_total_day": (("Общее количество порций питания в сутки",), HINT_NUMBER, True),
    "kitchen_distance_m": (("Среднее расстояние от пищеблока до отделения",), HINT_NUMBER, False),
    "meal_points": (("Количество точек раздачи питания (отделений)",), HINT_INTEGER, True),
    "meal_trolley_weight_kg": (("Средняя масса тележки с питанием (брутто)",), HINT_NUMBER, True),
    "meal_delivery_norm_min": (
        ("Норматив доставки питания (мин от пищеблока до отделения)",),
        HINT_NUMBER,
        False,
    ),
    "dirty_linen_kg_day": (("Объём грязного белья (кг/сутки)",), HINT_NUMBER, False),
    "clean_linen_kg_day": (("Объём чистого белья на раздачу (кг/сутки)",), HINT_NUMBER, False),
    "linen_points": (("Количество точек сбора/выдачи белья",), HINT_INTEGER, False),
    "linen_change_per_day": (
        ("Периодичность смены белья (раз в сутки, в среднем)",),
        HINT_NUMBER,
        False,
    ),
    "linen_container_kg": (("Средняя масса контейнера с бельём",), HINT_NUMBER, False),
    "med_item_names": (
        ("Количество наименований медикаментов в обращении",),
        HINT_INTEGER,
        False,
    ),
    "med_orders_day": (("Объём выдачи медикаментов (заявок/сутки)",), HINT_NUMBER, True),
    "pharmacy_points": (("Количество аптечных точек выдачи (аптека, аптечные склады)",), HINT_INTEGER, False),
    "med_delivery_points": (
        ("Количество точек доставки (отделений + ОР + реанимация)",),
        HINT_INTEGER,
        True,
    ),
    "med_pick_time_min": (("Среднее время комплектации 1 заявки в аптеке",), HINT_NUMBER, False),
    "stat_share_pct": (("Доля срочных (STAT) доставок медикаментов",), HINT_PERCENT, False),
    "supplies_runs_day": (("Объём доставки расходных материалов (рейсов/сутки)",), HINT_NUMBER, False),
    "samples_day": (("Количество биоматериалов (проб) в сутки",), HINT_NUMBER, False),
    "labs_count": (("Количество клинико-диагностических лабораторий (КДЛ)",), HINT_INTEGER, False),
    "sample_delivery_norm_min": (("Среднее время доставки пробы (норматив)",), HINT_NUMBER, False),
    "lab_results_runs_day": (("Объём выдачи результатов анализов (рейсов/сутки)",), HINT_NUMBER, False),
    "waste_a_kg_day": (("Объём медицинских отходов класса А (ненасыщенные)",), HINT_NUMBER, False),
    "waste_b_kg_day": (("Объём медицинских отходов класса Б (инфицированные)",), HINT_NUMBER, False),
    "waste_points": (("Количество точек сбора отходов",), HINT_INTEGER, False),
    "waste_removal_per_day": (("Периодичность вывоза отходов из отделений",), HINT_NUMBER, False),
    "sanitaries_headcount": (("Численность санитаров и транспортировщиков",), HINT_INTEGER, True),
    "kitchen_headcount": (("Численность сотрудников пищеблока (раздача)",), HINT_INTEGER, False),
    "laundry_headcount": (("Численность сотрудников прачечной (транспорт белья)",), HINT_INTEGER, False),
    "sanitary_salary_rub": (("Средняя з/п санитара/транспортировщика (gross)",), HINT_NUMBER, True),
    "kitchen_staff_salary_rub": (("Средняя з/п сотрудника пищеблока (gross)",), HINT_NUMBER, False),
    "disinfection_required": (("Обеззараживание робота между рейсами",), HINT_TEXT, False),
    "surface_requirement": (("Требования к материалу поверхностей робота",), HINT_TEXT, False),
    "has_mis": (("Наличие МИС (медицинская информационная система)",), HINT_TEXT, False),
    "has_lis": (("Наличие ЛИС (лабораторная информационная система)",), HINT_TEXT, False),
    "has_elevator_api": (("Наличие системы управления лифтами (BMS)",), HINT_TEXT, False),
    "corridor_width_m": (("Ширина коридоров (основных)",), HINT_NUMBER, True),
    "has_ramps": (
        ("Наличие пандусов/подъёмников (для межэтажного AMR без лифта)",),
        HINT_TEXT,
        False,
    ),
}

# Варианты для параметров со значением type = enum (подсказки из примечаний датасета).
ENUM_OPTIONS: dict[str, list[str]] = {
    "floor_covering": ["Промышленный бетон", "Эпоксидное покрытие", "Асфальт", "Полимерный наливной"],
    "racking_system": [
        "Фронтальные паллетные",
        "Стеллажи с операционными проходами",
        "Drive-in",
        "Push-back",
        "Глубинные (Deeper)",
        "Мезонины",
    ],
    "facility_type": [
        "Многопрофильная больница",
        "Поликлиника",
        "Онкоцентр",
        "Диагностический центр",
        "Районная больница",
    ],
}

# Коды секций (строки «▌ ...») → стабильный код группы.
GROUP_CODES: dict[str, str] = {
    "ОБЩИЕ ПАРАМЕТРЫ ОБЪЕКТА": "general",
    "РЕЖИМ РАБОТЫ": "work_mode",
    "ОПЕРАЦИИ: ОБЪЁМ И ПРОИЗВОДИТЕЛЬНОСТЬ": "operations",
    "ПЕРСОНАЛ": "staff",
    "МАРШРУТЫ И ПЛАНИРОВКА": "layout",
    "ХРАНЕНИЕ И ХАРАКТЕРИСТИКИ ГРУЗОВ": "storage",
    "ИНФРАСТРУКТУРА И ОГРАНИЧЕНИЯ": "infrastructure",
    "ПАССАЖИРСКИЙ ПОТОК": "passenger_flow",
    "АВИАЦИОННОЕ НАЗОМНОЕ ОБСЛУЖИВАНИЕ (RAMP)": "ramp",
    "ВНУТРИПОРТОВАЯ ЛОГИСТИКА И УБОРКА": "ground_logistics",
    "БЕЗОПАСНОСТЬ И ОГРАНИЧЕНИЯ": "safety",
    "ИНФРАСТРУКТУРА": "infrastructure",
    "ВНУТРИБОЛЬНИЧНАЯ ЛОГИСТИКА: ПИТАНИЕ": "meals",
    "ВНУТРИБОЛЬНИЧНАЯ ЛОГИСТИКА: БЕЛЬЁ": "linen",
    "ВНУТРИБОЛЬНИЧНАЯ ЛОГИСТИКА: МЕДИКАМЕНТЫ И РАСХОДНИКИ": "meds",
    "ВНУТРИБОЛЬНИЧНАЯ ЛОГИСТИКА: АНАЛИЗЫ И БИОМАТЕРИАЛЫ": "lab",
    "ВНУТРИБОЛЬНИЧНАЯ ЛОГИСТИКА: ОТХОДЫ": "waste",
    "ПЕРСОНАЛ (НЕМЕДИЦИНСКИЙ, ЗАДЕЙСТВОВАННЫЙ В ЛОГИСТИКЕ)": "staff",
    "ТРЕБОВАНИЯ БЕЗОПАСНОСТИ И САНИТАРНЫЕ НОРМЫ": "safety",
}


def normalize_name(name: str) -> str:
    """Приводит название параметра к ключу сравнения: без регистра и ё/е."""
    s = name.strip().lower().replace("ё", "е")
    s = re.sub(r"\s+", " ", s)
    return s


def _build_index() -> dict[str, str]:
    index: dict[str, str] = {}
    for code, (aliases, _hint, _req) in PARAM_CODES.items():
        for alias in aliases:
            index[normalize_name(alias)] = code
    return index


NAME_TO_CODE: dict[str, str] = _build_index()


def resolve_code(name: str) -> str | None:
    """Русское название параметра → код. None, если параметр не описан."""
    return NAME_TO_CODE.get(normalize_name(name))


def code_meta(code: str) -> tuple[str, bool]:
    """Код → (подсказка типа значения, обязателен ли параметр)."""
    _aliases, hint, required = PARAM_CODES[code]
    return hint, required


# Тот же словарь, но с нормализованными ключами — поиск идёт по lowercase.
_GROUP_INDEX: dict[str, str] = {
    normalize_name(name): code for name, code in GROUP_CODES.items()
}


def group_code(name: str) -> str:
    """Название секции → код группы (fallback — slug из латиницы)."""
    key = normalize_name(name).lstrip("▌ ").strip()
    if key in _GROUP_INDEX:
        return _GROUP_INDEX[key]
    return re.sub(r"[^a-z0-9]+", "_", key).strip("_") or "other"
