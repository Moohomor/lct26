"""Движок подбора решений.

Логика в два слоя:

1. Жёсткие ограничения (blocker) — если решение не проходит, оно не попадает
   в подборку вообще, а пользователю показывается причина с числами:
   «ширина прохода 1,5 м < требуемых 1,95 м».
2. Балльная оценка (0–100) — среди прошедших ограничения решения ранжируются
   по тому, насколько они подходят объекту: хватает ли производительности,
   разумна ли цена, подтверждены ли ТТХ, зрелая ли технология.

Результат сопровождается объяснением: у каждого решения есть и причины
«почему подходит», и предупреждения. Без объяснения подбор превращается в
чёрный ящик, а по ТЗ 3.4.2 пользователь должен понимать рекомендацию.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from app.models import Solution
from app.services.matching.requirements import Requirement, build_requirements

# Веса составляющих балльной оценки. Сумма = 100.
WEIGHT_FIT = 34          # производительности и грузоподъёмности хватает с запасом
WEIGHT_ECONOMY = 26      # стоимость единицы полезной работы
WEIGHT_DATA = 18         # полнота и подтверждённость ТТХ
WEIGHT_MATURITY = 12     # зрелость технологии
WEIGHT_MATCH = 10        # точное совпадение типа решения и процесса


@dataclass
class RequirementCheck:
    requirement_code: str
    label: str
    passed: bool
    severity: str
    #: человекочитаемое объяснение с числами
    message: str
    required: str | None = None
    actual: str | None = None


@dataclass
class MatchResult:
    solution: Solution
    score: float
    #: 0–100, насколько производительности хватает
    fit_score: float
    economy_score: float
    data_score: float
    maturity_score: float
    type_match_score: float
    checks: list[RequirementCheck] = field(default_factory=list)
    reasons: list[str] = field(default_factory=list)
    blockers: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    #: рекомендуемое число единиц по расчёту sizing
    recommended_quantity: int | None = None
    peak_demand: float | None = None
    demand_unit: str | None = None

    @property
    def is_eligible(self) -> bool:
        return not self.blockers

    def as_dict(self) -> dict[str, Any]:
        sol = self.solution
        return {
            "solution_id": str(sol.id),
            "name": sol.name,
            "vendor": sol.vendor.name if sol.vendor else None,
            "solution_type": (
                {"id": sol.solution_type_id, "code": sol.solution_type.code, "name": sol.solution_type.name}
                if sol.solution_type
                else None
            ),
            "status": sol.status,
            "is_eligible": self.is_eligible,
            "score": round(self.score, 1),
            "scores": {
                "fit": round(self.fit_score, 1),
                "economy": round(self.economy_score, 1),
                "data": round(self.data_score, 1),
                "maturity": round(self.maturity_score, 1),
                "type_match": round(self.type_match_score, 1),
            },
            "reasons": self.reasons,
            "blockers": self.blockers,
            "warnings": self.warnings,
            "checks": [
                {
                    "code": c.requirement_code,
                    "label": c.label,
                    "passed": c.passed,
                    "severity": c.severity,
                    "message": c.message,
                    "required": c.required,
                    "actual": c.actual,
                }
                for c in self.checks
            ],
            "recommended_quantity": self.recommended_quantity,
            "peak_demand": self.peak_demand,
            "demand_unit": self.demand_unit,
            "unit_price_rub": float(sol.unit_price_rub) if sol.unit_price_rub is not None else None,
            "price_source": sol.price_source,
            "completeness": float(sol.completeness or 0),
        }


def _num(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fmt(value: float | None, digits: int = 2) -> str:
    if value is None:
        return "—"
    return f"{value:,.{digits}f}".replace(",", " ").replace(".", ",")


# ─────────────────────────────────────────────────────────────────────────────
# Проверка требований
# ─────────────────────────────────────────────────────────────────────────────


def _unknown(req: Requirement, required: str, what: str) -> RequirementCheck:
    """Проверка, для которой в каталоге нет подтверждённого значения.

    Единое правило для всех проверок: отсутствие данных — это не отказ.
    Каталог организатора заполнен выборочно, и решение с незаполненной
    грузоподъёмностью не перестаёт быть решением. Если бы «нет данных» значило
    «не подходит», подбор на реальном каталоге возвращал бы пустоту: из 190
    позиций склада половина отсеивалась бы не по существу, а по пробелу в
    анкете.

    Отказом такое требование не считается, но оно попадает в предупреждения и
    снимает баллы в компоненте «полнота данных» — пользователь видит, что
    характеристику нужно подтвердить у поставщика, и решение остаётся в
    выдаче.
    """
    return RequirementCheck(
        requirement_code=req.code,
        label=req.label,
        passed=False,
        severity="warning",
        message=f"{req.label}: {what} — подтвердите по документации поставщика",
        required=required,
        actual=None,
    )


def _check_payload(req: Requirement, sol: Solution) -> RequirementCheck:
    actual = _num(sol.payload_kg)
    need = req.minimum or 0.0
    if actual is None:
        return _unknown(req, f"≥ {_fmt(need, 0)} кг", "грузоподъёмность в данных не указана")
    ok = actual >= need - 1e-9
    return RequirementCheck(
        requirement_code=req.code,
        label=req.label,
        passed=ok,
        severity=req.severity,
        message=f"Грузоподъёмность {_fmt(actual, 0)} кг против требуемых {_fmt(need, 0)} кг",
        required=f"≥ {_fmt(need, 0)} кг",
        actual=f"{_fmt(actual, 0)} кг",
    )


def _check_passage(req: Requirement, sol: Solution, object_type: str) -> RequirementCheck:
    available = req.maximum or 0.0
    actual = _num(sol.min_passage_width_m)
    # У стационарных систем (AS/RS, шаттл) прохода не нужно: они занимают
    # отведённую зону, а не ездят по коридору.
    needs_passage = sol.solution_type.requires_passage if sol.solution_type else True
    if not needs_passage:
        return RequirementCheck(
            requirement_code=req.code,
            label=req.label,
            passed=True,
            severity="info",
            message="Стационарная система: требование к ширине проезда не применяется",
            required=f"≤ {_fmt(available)} м",
            actual="не требуется",
        )
    if actual is None:
        # Габариты известны — считаем проход из них.
        width = _num(sol.width_m)
        if width is not None:
            margin = float(sol.solution_type.passage_margin_m) if sol.solution_type else 0.3
            actual = width + margin
        else:
            return _unknown(
                req, f"≤ {_fmt(available)} м", "габариты не указаны, проезд проверить нельзя"
            )
    ok = actual <= available + 1e-9
    return RequirementCheck(
        requirement_code=req.code,
        label=req.label,
        passed=ok,
        severity=req.severity,
        message=(
            f"Требуемый проезд {_fmt(actual)} м (с запасом) при доступной ширине {_fmt(available)} м"
            if not ok
            else f"Проезд {_fmt(actual)} м укладывается в доступные {_fmt(available)} м"
        ),
        required=f"≤ {_fmt(available)} м",
        actual=f"{_fmt(actual)} м",
    )


def _check_maximum(req: Requirement, sol: Solution) -> RequirementCheck:
    """Требование вида «не более X» (шум, отклонение пола, ширина)."""
    limit = req.maximum or 0.0
    actual = _num(getattr(sol, _SOLUTION_FIELD.get(req.code, ""), None))
    if actual is None:
        return _unknown(req, f"≤ {_fmt(limit)}", "подтверждённое значение в данных отсутствует")
    ok = actual <= limit + 1e-9
    return RequirementCheck(
        requirement_code=req.code,
        label=req.label,
        passed=ok,
        severity=req.severity,
        message=f"{req.label}: {_fmt(actual)} против предела {_fmt(limit)}",
        required=f"≤ {_fmt(limit)}",
        actual=f"{_fmt(actual)}",
    )


def _check_minimum(req: Requirement, sol: Solution) -> RequirementCheck:
    """Требование вида «не менее X» (температура сверху, автономность)."""
    need = req.minimum or 0.0
    field_name = _SOLUTION_FIELD.get(req.code, "")
    actual = _num(getattr(sol, field_name, None)) if field_name else None
    if req.code == "temperature":
        # Температура — диапазон: решение должно работать и на перроне зимой.
        min_t = _num(sol.min_temp_c)
        max_t = _num(sol.max_temp_c)
        if min_t is None and max_t is None:
            return _unknown(
                req, f"≤ {_fmt(need, 0)} °C", "диапазон рабочих температур не указан"
            )
        ok = (max_t is not None and max_t <= need + 1e-9) or (
            min_t is not None and min_t <= need + 1e-9
        )
        return RequirementCheck(
            requirement_code=req.code,
            label=req.label,
            passed=ok,
            severity=req.severity,
            message=(
                f"Рабочий диапазон {_fmt(min_t, 0)}…{_fmt(max_t, 0)} °C "
                f"против режима объекта (до {_fmt(need, 0)} °C)"
            ),
            required=f"≤ {_fmt(need, 0)} °C",
            actual=f"{_fmt(min_t, 0)}…{_fmt(max_t, 0)} °C",
        )
    if actual is None:
        return _unknown(req, f"≥ {_fmt(need)}", "значение не подтверждено")
    ok = actual >= need - 1e-9
    return RequirementCheck(
        requirement_code=req.code,
        label=req.label,
        passed=ok,
        severity=req.severity,
        message=f"{req.label}: {_fmt(actual)} против требуемых {_fmt(need)}",
        required=f"≥ {_fmt(need)}",
        actual=f"{_fmt(actual)}",
    )


def _check_flag(req: Requirement, sol: Solution) -> RequirementCheck:
    """Требования-признаки: допуск в режимные зоны, санитарная обработка."""
    field_name = {
        "airside_cert": "airside_certified",
        "sanitation": "medical_sanitation_ready",
    }.get(req.code)
    actual = getattr(sol, field_name, None) if field_name else None
    if actual is None:
        return _unknown(req, "подтверждено", "подтверждение в данных отсутствует")
    return RequirementCheck(
        requirement_code=req.code,
        label=req.label,
        passed=bool(actual),
        severity=req.severity,
        message=f"{req.label}: {'подтверждено' if actual else 'не подтверждено'}",
        required="подтверждено",
        actual="да" if actual else "нет",
    )


def _check_generic(req: Requirement, sol: Solution) -> RequirementCheck:
    """Требования, которые нельзя проверить по ТТХ: интеграции и рекомендации."""
    return RequirementCheck(
        requirement_code=req.code,
        label=req.label,
        passed=True,
        severity=req.severity,
        message=req.format_text({}),
    )


# Код требования → поле ТТХ решения, по которому оно проверяется.
_SOLUTION_FIELD = {
    "noise": "max_noise_dba",
    "floor_roughness": "max_floor_roughness_mm",
    "power": "charge_power_kw",
    "autonomy": "autonomy_hours",
    "temperature": "min_temp_c",
}


def evaluate(sol: Solution, requirements: list[Requirement], object_type: str) -> list[RequirementCheck]:
    checks: list[RequirementCheck] = []
    for req in requirements:
        if req.code == "payload":
            checks.append(_check_payload(req, sol))
        elif req.code == "passage":
            checks.append(_check_passage(req, sol, object_type))
        elif req.severity in {"warning", "info"} and req.maximum is not None:
            checks.append(_check_maximum(req, sol))
        elif req.minimum is not None:
            checks.append(_check_minimum(req, sol))
        elif req.code in {"airside_cert", "sanitation"}:
            checks.append(_check_flag(req, sol))
        else:
            checks.append(_check_generic(req, sol))
    return checks


# ─────────────────────────────────────────────────────────────────────────────
# Балльная оценка
# ─────────────────────────────────────────────────────────────────────────────


def _fit_score(sol: Solution, peak_demand: float | None, unit: str | None) -> tuple[float, str | None]:
    """Достаточно ли производительности решения.

    Возвращает балл и текст с запасом мощности — именно этот текст чаще всего
    объясняет, почему одно решение предпочтительнее другого.
    """
    if not peak_demand or peak_demand <= 0:
        return 70.0, None
    thr = _num(sol.throughput_per_hour)
    if thr is None or thr <= 0:
        return 35.0, None
    ratio = thr / peak_demand
    if ratio < 1.0:
        # Недостаточная производительность: это блокер, а не низкий балл.
        return 0.0, (
            f"Производительность {_fmt(thr, 0)} {unit or ''} ниже пиковой потребности "
            f"{_fmt(peak_demand, 0)} {unit or ''}"
        )
    # Запас 1,0 → 60 баллов, запас 2,0 и выше → 100 баллов.
    score = min(100.0, 60.0 + 40.0 * (ratio - 1.0))
    return score, (
        f"Запас производительности ×{_fmt(ratio, 1)}: "
        f"{_fmt(thr, 0)} {unit or ''} против пиковой потребности "
        f"{_fmt(peak_demand, 0)} {unit or ''}"
    )


def _economy_score(sol: Solution, peak_demand: float | None, unit: str | None) -> tuple[float, str | None]:
    """Стоимость единицы полезной работы — основной аргумент при сравнении."""
    price = _num(sol.unit_price_rub)
    if price is None or price <= 0:
        return 25.0, None
    if not peak_demand or peak_demand <= 0:
        return 60.0, None
    cost_per_unit = price / peak_demand
    # 10 000 руб./ед. — 100 баллов; 100 000 руб./ед. — 20 баллов (логарифм).
    import math

    score = 100.0 - 40.0 * min(1.0, max(0.0, math.log10(cost_per_unit / 1e4 + 1) / 1.0))
    return max(0.0, min(100.0, score)), (
        f"Удельная стоимость {_fmt(cost_per_unit, 0)} руб. на единицу работы "
        f"({unit or 'ед.'})"
    )


def _data_score(sol: Solution) -> tuple[float, str | None]:
    completeness = float(sol.completeness or 0)
    score = min(100.0, completeness)
    if sol.is_verified:
        score = min(100.0, score + 15.0)
        return score, "ТТХ подтверждены источником организатора"
    if completeness < 30:
        return score, "ТТХ заполнены частично — расчёт предварительный"
    return score, None


def _maturity_score(sol: Solution) -> tuple[float, str | None]:
    status_points = {"operation": 100.0, "piloting": 70.0, "rnd": 35.0, "development": 45.0}
    base = status_points.get(sol.status, 50.0)
    trl = sol.trl
    if trl:
        base = 0.5 * base + 0.5 * (trl / 9.0 * 100.0)
    note = None
    if sol.status == "rnd":
        note = "Статус R&D: решение на стадии разработки, риск внедрения выше"
    elif sol.status == "piloting":
        note = "Статус «пилотирование»: подтверждённых внедрений пока мало"
    return min(100.0, base), note


def _type_match_score(sol: Solution, process_code: str) -> tuple[float, str | None]:
    codes = sol.process_codes or []
    if not codes:
        return 40.0, "Процесс применения в данных не указан — проверьте вручную"
    if process_code in codes:
        return 100.0, None
    # Процесс не указан, но объект совпадает — частичное совпадение.
    if sol.applicable_object_types:
        return 60.0, "Тип объекта подходит, но процесс в карточке не указан"
    return 40.0, "Решение не привязано к этому типу объекта"


def score_solution(
    sol: Solution,
    object_type: str,
    process_code: str,
    requirements: list[Requirement],
    peak_demand: float | None,
    demand_unit: str | None,
) -> MatchResult:
    checks = evaluate(sol, requirements, object_type)

    blockers: list[str] = []
    warnings: list[str] = []
    for check in checks:
        if check.passed:
            continue
        if check.severity == "blocker":
            blockers.append(check.message)
        elif check.severity == "warning":
            warnings.append(check.message)

    fit_score, fit_note = _fit_score(sol, peak_demand, demand_unit)
    if fit_note and fit_score <= 0:
        blockers.append(fit_note)
    economy_score, economy_note = _economy_score(sol, peak_demand, demand_unit)
    data_score, data_note = _data_score(sol)
    maturity_score, maturity_note = _maturity_score(sol)
    type_score, type_note = _type_match_score(sol, process_code)

    total = (
        fit_score * WEIGHT_FIT
        + economy_score * WEIGHT_ECONOMY
        + data_score * WEIGHT_DATA
        + maturity_score * WEIGHT_MATURITY
        + type_score * WEIGHT_MATCH
    ) / 100.0

    reasons = [n for n in (fit_note, economy_note, data_note, type_note) if n]
    if maturity_note:
        warnings.append(maturity_note)
    if sol.price_source == "estimate":
        warnings.append("Цена — оценочное допущение, требуется коммерческое предложение")
    if sol.is_variant_of_id is not None:
        warnings.append("Это комплектация другого решения из каталога — проверьте состав")

    quantity: int | None = None
    if peak_demand and peak_demand > 0:
        thr = _num(sol.throughput_per_hour)
        if thr and thr > 0:
            from app.services.economics.sizing import required_units

            quantity = required_units(
                peak_demand=peak_demand,
                unit_productivity=thr,
                load_factor=0.80,
                availability=0.95,
            )

    return MatchResult(
        solution=sol,
        score=total,
        fit_score=fit_score,
        economy_score=economy_score,
        data_score=data_score,
        maturity_score=maturity_score,
        type_match_score=type_score,
        checks=checks,
        reasons=reasons,
        blockers=blockers,
        warnings=warnings,
        recommended_quantity=quantity,
        peak_demand=peak_demand,
        demand_unit=demand_unit,
    )


def rank(
    solutions: list[Solution],
    object_type: str,
    process_code: str,
    params: dict,
) -> dict[str, Any]:
    """Полный результат подбора: требования, ранжирование, сводка по процессам."""
    requirements, peak_demand, demand_unit = build_requirements(object_type, process_code, params)

    results = [
        score_solution(sol, object_type, process_code, requirements, peak_demand, demand_unit)
        for sol in solutions
    ]
    results.sort(key=lambda r: (r.is_eligible, r.score), reverse=True)

    eligible = [r for r in results if r.is_eligible]

    return {
        "object_type": object_type,
        "process": process_code,
        "requirements": [
            {
                "code": r.code,
                "label": r.label,
                "severity": r.severity,
                "unit": r.unit,
                "minimum": r.minimum,
                "maximum": r.maximum,
                "source_param": r.source_param,
                "text": r.format_text(params),
            }
            for r in requirements
        ],
        "peak_demand": peak_demand,
        "demand_unit": demand_unit,
        "results": [r.as_dict() for r in results],
        "summary": {
            "considered": len(results),
            "eligible": len(eligible),
            "rejected": len(results) - len(eligible),
            "top_score": round(eligible[0].score, 1) if eligible else None,
        },
        "weights": {
            "fit": WEIGHT_FIT,
            "economy": WEIGHT_ECONOMY,
            "data": WEIGHT_DATA,
            "maturity": WEIGHT_MATURITY,
            "type_match": WEIGHT_MATCH,
        },
    }
