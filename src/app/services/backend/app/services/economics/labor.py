"""Базовая модель трудозатрат: сколько стоит персонал сейчас и сколько ставок
замещает роботизация.

Три решения, которые делают расчёт проверяемым, а не приукрашивающим:

1. Каждая штатная единица связана со своей ставкой. Раньше для любой роли
   подставлялась первая найденная зарплата объекта, из-за чего водитель
   погрузчика считался по ставке сборщика.
2. `total_headcount` — это весь штат, а подроли (`pickers_headcount` и т. п.) —
   его разбивка. Складывать их нельзя: получился бы двойной счёт. Если в
   объекте задан только общий штат, он и используется как верхняя оценка.
3. Базовый сценарий «до роботизации» считается по тем ролям, которые
   задействованы в выбранных для роботизации процессах, а не по всему
   персоналу объекта: сравнивать нужно тот кусок работы, который меняется.

Доля замещения по каждому процессу — явное допущение с обоснованием; оно
попадает в отчёт и может быть переопределено администратором.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Процесс → (какая штатная единица замещается, максимальная доля замещения,
#             обоснование доли)
PROCESS_LABOR: dict[tuple[str, str], tuple[str, float, str]] = {
    ("warehouse", "picking"): (
        "pickers_headcount", 0.70,
        "Робот закрывает до 70 % операций отбора; объём, требующий ручного "
        "обращения с нестандартным грузом, остаётся за людьми.",
    ),
    ("warehouse", "sorting"): (
        "pickers_headcount", 0.50,
        "Автоматическая сортировка берёт на себя стандартные потоки, "
        "ручная остаётся для нестандартных отправлений.",
    ),
    ("warehouse", "intra_logistics"): (
        "forklift_ops_headcount", 0.60,
        "Внутрискладские перевозки автоматизируются в большей части, "
        "но погрузка и стеллажирование остаются частично ручными.",
    ),
    ("warehouse", "receiving"): (
        "forklift_ops_headcount", 0.50,
        "Приёмка автоматизируется в части разгрузки и перемещения.",
    ),
    ("warehouse", "shipping"): (
        "forklift_ops_headcount", 0.55,
        "Погрузка комплектованных партий автоматизируется частично.",
    ),
    ("warehouse", "cleaning"): (
        "total_headcount", 0.03,
        "Уборка роботами экономит уборщиков; их доля в штате склада невелика.",
    ),
    ("warehouse", "storage"): (
        "forklift_ops_headcount", 0.40,
        "Стеллажирование адресное автоматизируется частично.",
    ),
    ("warehouse", "inventory"): (
        "total_headcount", 0.05,
        "Автоматизированная инвентаризация сокращает ручные пересчёты.",
    ),
    ("warehouse", "manufacturing"): (
        "total_headcount", 0.15,
        "Приланочное обслуживание роботами снижает нагрузку на операторов.",
    ),

    ("airport", "ground_handling"): (
        "ramp_headcount", 0.55,
        "Буксировка и часть наземных операций автоматизируются; работы "
        "с бортом по правилам аэродрома остаются за персоналом.",
    ),
    ("airport", "baggage"): (
        "ramp_headcount", 0.60,
        "Транспортировка и первичная сортировка багажа автоматизируются, "
        "погрузка в багажный отсек — нет.",
    ),
    ("airport", "catering"): (
        "ramp_headcount", 0.45,
        "Доставка питания на борт автоматизируется частично: загрузка "
        "и стыковка остаются за персоналом.",
    ),
    ("airport", "terminal_logistics"): (
        "terminal_headcount", 0.50,
        "Внутритерминальные перевозки — основной эффект AMR.",
    ),
    ("airport", "ground_cleaning"): (
        "terminal_headcount", 0.06,
        "Роботы-уборщики сокращают штат уборщиков терминала.",
    ),
    ("airport", "waste"): (
        "terminal_headcount", 0.05,
        "Вывоз контейнеров автоматизируется частично.",
    ),

    ("medical", "meals"): (
        "kitchen_headcount", 0.55,
        "Доставка питания от пищеблока — типовой сценарий AMR; раздача "
        "в палатах остаётся за персоналом.",
    ),
    ("medical", "linen"): (
        "laundry_headcount", 0.60,
        "Сбор и доставка белья автоматизируются в части транспортировки.",
    ),
    ("medical", "meds"): (
        "sanitaries_headcount", 0.35,
        "Транспортировка заявок автоматизируется, комплектация в аптеке — нет.",
    ),
    ("medical", "lab"): (
        "sanitaries_headcount", 0.40,
        "Доставка проб и результатов — типовой сценарий AMR в больнице.",
    ),
    ("medical", "waste"): (
        "sanitaries_headcount", 0.35,
        "Вывоз отходов автоматизируется в части транспортировки.",
    ),
    ("medical", "supplies"): (
        "sanitaries_headcount", 0.25,
        "Доставка расходных материалов автоматизируется частично.",
    ),
    ("medical", "cleaning"): (
        "sanitaries_headcount", 0.20,
        "Роботы-уборщики высвобождают часть санитаров.",
    ),
}

# Штатная единица → код параметра с её численностью и кодом с её ставкой.
# Одна и та же единица может встречаться в процессах разных типов объектов,
# поэтому коды ставок различаются по типу объекта.
ROLE_PARAMS: dict[str, dict[str, tuple[str, str | None]]] = {
    "pickers_headcount": {
        "warehouse": ("pickers_headcount", "picker_salary_rub"),
    },
    "forklift_ops_headcount": {
        "warehouse": ("forklift_ops_headcount", "forklift_salary_rub"),
    },
    "packing_ops_headcount": {
        "warehouse": ("packing_ops_headcount", None),
    },
    "total_headcount": {
        "warehouse": ("total_headcount", None),
        "airport": ("total_headcount", None),
        "medical": ("total_headcount", None),
    },
    "ramp_headcount": {
        "airport": ("ramp_headcount", "ramp_salary_rub"),
    },
    "terminal_headcount": {
        "airport": ("terminal_headcount", "cleaner_salary_rub"),
    },
    "sanitaries_headcount": {
        "medical": ("sanitaries_headcount", "sanitary_salary_rub"),
    },
    "kitchen_headcount": {
        "medical": ("kitchen_headcount", "kitchen_staff_salary_rub"),
    },
    "laundry_headcount": {
        "medical": ("laundry_headcount", None),
    },
}

ROLE_LABELS: dict[str, str] = {
    "pickers_headcount": "Сборщики заказов",
    "forklift_ops_headcount": "Операторы погрузчиков",
    "packing_ops_headcount": "Упаковщики",
    "total_headcount": "Прочие сотрудники",
    "ramp_headcount": "Персонал перрона",
    "terminal_headcount": "Персонал терминала",
    "sanitaries_headcount": "Санитары",
    "kitchen_headcount": "Сотрудники пищеблока",
    "laundry_headcount": "Сотрудники прачечной",
}

# Ставка-заменитель, если для роли отдельной ставки в датасете нет.
FALLBACK_SALARY_SOURCE = {
    "warehouse": "picker_salary_rub",
    "airport": "ramp_salary_rub",
    "medical": "sanitary_salary_rub",
}

MONTHS_PER_YEAR = 12


def _num(params: dict, code: str | None) -> float | None:
    if not code:
        return None
    value = params.get(code)
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


@dataclass
class RoleCost:
    role: str
    label: str
    headcount: float
    monthly_salary: float
    salary_source: str
    annual_cost: float
    #: True, если оценка получена из общего штата, а не из подроли
    is_aggregate: bool = False

    def as_dict(self) -> dict:
        return {
            "role": self.role,
            "label": self.label,
            "headcount": self.headcount,
            "monthly_salary": round(self.monthly_salary, 2),
            "salary_source": self.salary_source,
            "annual_cost": round(self.annual_cost, 2),
            "is_aggregate": self.is_aggregate,
        }


@dataclass
class LaborModel:
    roles: list[RoleCost] = field(default_factory=list)
    payroll_multiplier: float = 1.302
    annual_total: float = 0.0
    #: роли, для которых не удалось определить численность
    missing_headcount: list[str] = field(default_factory=list)

    def role(self, name: str) -> RoleCost | None:
        for r in self.roles:
            if r.role == name:
                return r
        return None

    @property
    def headcount_total(self) -> float:
        return sum(r.headcount for r in self.roles)

    def as_dict(self) -> dict:
        return {
            "payroll_multiplier": self.payroll_multiplier,
            "annual_total": round(self.annual_total, 2),
            "headcount_total": round(self.headcount_total, 1),
            "roles": [r.as_dict() for r in self.roles],
            "missing_headcount": self.missing_headcount,
        }


def _salary_for(
    role: str, object_type: str, params: dict
) -> tuple[float, str]:
    """Ставка для роли и указание, откуда она взята."""
    entry = ROLE_PARAMS.get(role, {}).get(object_type)
    salary_code = entry[1] if entry else None
    if salary_code:
        salary = _num(params, salary_code)
        if salary:
            return salary, salary_code
    fallback_code = FALLBACK_SALARY_SOURCE.get(object_type)
    fallback = _num(params, fallback_code) if fallback_code else None
    if fallback:
        return fallback, f"резервная ставка объекта ({fallback_code})"
    return 0.0, "ставка в датасете не указана"


def roles_for_processes(object_type: str, process_codes: list[str]) -> list[str]:
    """Штатные единицы, задействованные в выбранных процессах, без повторов."""
    roles: list[str] = []
    for code in process_codes:
        spec = PROCESS_LABOR.get((object_type, code))
        if spec and spec[0] not in roles:
            roles.append(spec[0])
    return roles


def build_baseline_labor(
    object_type: str,
    params: dict,
    payroll_multiplier: float,
    salary_multiplier: float = 1.0,
    process_codes: list[str] | None = None,
) -> LaborModel:
    """Годовая стоимость персонала, выполняющего роботизируемые операции.

    Если передан `process_codes`, считается только персонал этих процессов —
    это честная база для сравнения «до / после». Без него берётся весь штат
    объекта, что годится лишь для верхней оценки затрат.
    """
    model = LaborModel(payroll_multiplier=payroll_multiplier)
    multiplier = payroll_multiplier * salary_multiplier

    if process_codes:
        roles = roles_for_processes(object_type, process_codes)
    else:
        roles = [
            role
            for role, mapping in ROLE_PARAMS.items()
            if object_type in mapping
        ]

    # Если численность подроли не задана, но известен общий штат — берём его
    # как ориентир и честно помечаем оценку агрегированной.
    total_headcount = _num(params, "total_headcount")
    added_aggregate = False

    for role in roles:
        entry = ROLE_PARAMS.get(role, {}).get(object_type)
        headcount_code = entry[0] if entry else role
        headcount = _num(params, headcount_code)
        is_aggregate = False
        if not headcount and total_headcount and not added_aggregate:
            headcount = total_headcount
            is_aggregate = True
            added_aggregate = True
        if not headcount:
            model.missing_headcount.append(ROLE_LABELS.get(role, role))
            continue
        salary, source = _salary_for(role, object_type, params)
        if salary <= 0:
            model.missing_headcount.append(ROLE_LABELS.get(role, role))
        model.roles.append(
            RoleCost(
                role=role,
                label=ROLE_LABELS.get(role, role),
                headcount=headcount,
                monthly_salary=salary,
                salary_source=source,
                annual_cost=headcount * salary * MONTHS_PER_YEAR * multiplier,
                is_aggregate=is_aggregate,
            )
        )
        model.annual_total += headcount * salary * MONTHS_PER_YEAR * multiplier

    return model


def labor_saving_for_process(
    object_type: str,
    process_code: str,
    params: dict,
    robots: int,
    fte_per_robot: float,
    payroll_multiplier: float,
    salary_multiplier: float = 1.0,
) -> dict[str, Any]:
    """Экономия ФОТ от внедрения `robots` единиц оборудования в один процесс.

    Замещается не более `max_replacement_share` штатной единицы: робот
    автоматизирует типовые операции процесса, но не всю работу человека.
    """
    spec = PROCESS_LABOR.get((object_type, process_code))
    if spec is None:
        return {
            "process": process_code,
            "supported": False,
            "replacement_fte": 0.0,
            "max_replacement_share": 0.0,
            "annual_saving": 0.0,
            "note": (
                "Для этого процесса доля замещения персонала не определена: "
                "эффект рассчитывается только по CAPEX/OPEX."
            ),
        }

    role, max_share, rationale = spec
    entry = ROLE_PARAMS.get(role, {}).get(object_type)
    headcount_code = entry[0] if entry else role
    headcount = _num(params, headcount_code)
    is_aggregate = False
    if not headcount:
        headcount = _num(params, "total_headcount")
        is_aggregate = True

    requested = robots * fte_per_robot
    if headcount:
        replacement = min(requested, headcount * max_share)
    else:
        replacement = 0.0
        rationale += (
            " Численность персонала в объекте не указана — эффект по ФОТ не рассчитан."
        )

    salary, salary_source = _salary_for(role, object_type, params)
    annual = replacement * salary * MONTHS_PER_YEAR * payroll_multiplier * salary_multiplier

    notes: list[str] = []
    if is_aggregate and headcount:
        notes.append(
            f"Численность роли «{ROLE_LABELS.get(role, role)}» в объекте не указана — "
            "использован общий штат как ориентир."
        )
    if replacement < requested:
        notes.append(
            f"Замещается {replacement:.1f} из {requested:.1f} ставки: доля замещения "
            f"ограничена {max_share:.0%} от численности роли."
        )

    return {
        "process": process_code,
        "supported": True,
        "role": role,
        "role_label": ROLE_LABELS.get(role, role),
        "role_headcount": headcount,
        "role_headcount_source": "total_headcount" if is_aggregate else headcount_code,
        "replacement_fte": round(replacement, 2),
        "requested_fte": round(requested, 2),
        "max_replacement_share": max_share,
        "salary_rub": salary,
        "salary_source": salary_source,
        "annual_saving": round(annual, 2),
        "rationale": rationale,
        "notes": notes,
    }
