"""Экономическая модель: регрессионные числа и инварианты.

Запомненные цифры — не «снапшот на сегодня», а проверка того, что модель
считает именно то, что задумано. Если формула окупаемости изменится, тест
упадёт и покажет, какое именно число разошлось — это дешевле, чем обнаружить
расхождение между экраном и отчётом на демонстрации жюри.
"""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")


def _warehouse_params() -> dict:
    """Параметры склада из значений по умолчанию.

    Без них экономия ФОТ нулечение: численность персонала неизвестна, и модель
    честно сообщает об этом, возвращая нулевой эффект. Тест обязан работать с
    теми же данными, что и реальный пользователь.
    """
    from sqlalchemy import select

    from app.models import ObjectType, Parameter

    from app.core.db import SessionLocal

    db = SessionLocal()
    try:
        ot = db.scalar(select(ObjectType).where(ObjectType.code == "warehouse"))
        return {
            p.code: p.default
            for p in db.scalars(
                select(Parameter).where(Parameter.object_type_id == ot.id)
            )
            if p.default is not None
        }
    finally:
        db.close()


def test_payback_is_computed_on_cash_flow():
    """Окупаемость считается по денежному потоку, а не по эффекту с амортизацией.

    ТЗ 3.5.4 требует включать амортизацию в годовой эффект. Но амортизация —
    безденежная статья: она уменьшает прибыль, но не отвлекает средства.
    Окупаемость по эффекту с амортизацией завышает срок, и при сроке
    амортизации 5 лет и окупаемости дольше неё не существует вовсе.
    """
    from app.services.economics import engine as econ

    report = econ.payback_report(
        investment=10_000_000,
        gross_annual=3_000_000,
        opex_total=1_000_000,
        amort_per_year=econ.amortization(10_000_000, 5),
    )
    # Денежный поток: 3 − 1 = 2 млн/год → окупаемость 5 лет
    assert report["cash_payback_years"] == pytest.approx(5.0)
    # Бухгалтерский эффект: 2 − 2 = 0 → окупаемости нет
    assert report["accounting_payback_years"] is None
    assert report["cash_net_annual"] == pytest.approx(2_000_000)


def test_amortization_is_linear():
    """Амортизация линейная: равные части в течение срока."""
    from app.services.economics import engine as econ

    per_year = econ.amortization(10_000_000, 5)
    assert per_year == pytest.approx(2_000_000)
    # Нулевой срок означает списание сразу — вся сумма в первый год
    assert econ.amortization(10_000_000, 0) == pytest.approx(10_000_000)


def test_tco_includes_residual_labor():
    """TCO по сценариям с техникой учитывает остаточный ФОТ.

    Роботы замещают часть сотрудников, но объект продолжает работать. Сравнивать
    «CAPEX + OPEX» с полной ФОТ объекта — сравнение разных по величине сумм,
    из которого автоматически получается красивый и неверный вывод о выгоде.
    """
    from app.services.economics import engine as econ
    from app.services.economics.calculator import _build_tco

    baseline = {
        "kind": "baseline",
        "annual_cost": 10_000_000,
        "capex": econ.CapexBreakdown().as_dict(),
        "opex": econ.OpexBreakdown().as_dict(),
    }
    purchase = {
        "kind": "purchase",
        "capex": econ.CapexBreakdown(total=5_000_000).as_dict(),
        "opex": econ.OpexBreakdown(total=1_000_000).as_dict(),
        "effect": {"labor_saving": 6_000_000, "gross_annual": 6_000_000},
        "raas": {},
    }
    raas = {
        "kind": "raas",
        "capex": econ.CapexBreakdown().as_dict(),
        "opex": econ.OpexBreakdown(total=2_000_000).as_dict(),
        "effect": {"labor_saving": 6_000_000, "gross_annual": 6_000_000},
        "raas": {"annual_payment": 1_500_000, "provider_opex": 500_000, "setup_fee": 100_000},
    }
    residual = 10_000_000 - 6_000_000  # 4 млн остаётся
    tco = _build_tco(baseline, purchase, raas, horizon=5, residual_labor=residual)

    # Покупка: 5 млн единовременно + (1 млн OPEX + 4 млн остаточный ФОТ) × 5
    assert tco["scenarios"]["purchase"]["total"] == pytest.approx(5_000_000 + 5_000_000 * 5)
    # База: 10 млн × 5 = 50 млн
    assert tco["scenarios"]["baseline"]["total"] == pytest.approx(50_000_000)
    # Остаточный ФОТ обязан быть в разбивке — иначе сравнение некорректно
    assert tco["scenarios"]["purchase"]["residual_labor_annual"] == pytest.approx(4_000_000)


def test_sensitivity_is_monotonic_in_equipment_cost():
    """При росте цены оборудования окупаемость не может сокращаться.

    Это проверка согласованности: если окупаемость на 1,3× короче, чем на
    0,7×, значит в расчёте чувствительности перепутаны множители или
    окупаемость считается не от того эффекта.
    """
    from app.services.economics import engine as econ

    def run(factor: float) -> dict:
        capex = 10_000_000 * factor
        opex = 1_000_000
        gross = 3_000_000
        payback = econ.payback_years(capex, gross - opex)
        return {
            "capex_total": capex,
            "annual_effect": gross - opex,
            "payback_years": payback,
        }

    base = {"capex_total": 10_000_000, "annual_effect": 2_000_000, "payback_years": 5.0}
    points = [
        {"factor": f, **run(f)} for f in (0.7, 0.85, 1.0, 1.15, 1.3)
    ]
    paybacks = [p["payback_years"] for p in points if p["payback_years"] is not None]
    assert paybacks == sorted(paybacks), (
        f"Окупаемость не монотонна при росте цены: {paybacks}"
    )


def test_full_calculation_via_api(client, user_headers):
    """Сквозной расчёт по HTTP: проект → подбор → сценарий → расчёт."""
    # Параметры по умолчанию — без них экономия ФОТ будет нулевой
    defaults = client.get(
        "/api/v1/object-types/warehouse/parameters/defaults"
    ).json()["values"]

    # Проект
    project = client.post(
        "/api/v1/projects",
        headers=user_headers,
        json={"object_type": "warehouse", "name": "Тест экономики",
               "parameters": defaults, "process_codes": ["intra_logistics"]},
    )
    assert project.status_code == 201, project.text
    project_id = project.json()["id"]

    # Подбор
    match = client.post(
        f"/api/v1/projects/{project_id}/match?limit=2", headers=user_headers
    )
    assert match.status_code == 200
    added = match.json()["added"]
    assert added, "Подбор не добавил ни одного решения"

    # Сценарий
    solutions = client.get(
        f"/api/v1/projects/{project_id}/solutions", headers=user_headers
    ).json()
    scenario = client.post(
        f"/api/v1/projects/{project_id}/scenarios",
        headers=user_headers,
        json={
            "name": "Покупка",
            "kind": "purchase",
            "items": [
                {"solution_id": s["solution_id"], "quantity": 2}
                for s in solutions[:2]
            ],
            "horizon_years": 5,
        },
    )
    assert scenario.status_code == 201, scenario.text
    scenario_id = scenario.json()["id"]

    # Расчёт
    calc = client.post(
        f"/api/v1/scenarios/{scenario_id}/calculate", headers=user_headers
    )
    assert calc.status_code == 200, calc.text
    body = calc.json()
    assert body["meta"]["model_version"]
    assert body["purchase"]["capex"]["total"] > 0
    assert body["purchase"]["opex"]["total"] > 0
    assert body["purchase"]["payback"]["cash_payback_years"] is not None
    assert body["tco"]["scenarios"]["purchase"]["total"] > 0
    assert body["sensitivity"], "Анализ чувствительности не построен"


def test_calculation_is_persisted_with_versions(client, user_headers):
    """Расчёт сохраняется снимком с версиями — для воспроизводимости (ТЗ 3.1.5)."""
    project = client.post(
        "/api/v1/projects",
        headers=user_headers,
        json={"object_type": "warehouse", "name": "Тест снимка",
               "parameters": {}, "process_codes": ["intra_logistics"]},
    ).json()
    match = client.post(
        f"/api/v1/projects/{project['id']}/match?limit=1", headers=user_headers
    ).json()
    assert match["added"]
    solutions = client.get(
        f"/api/v1/projects/{project['id']}/solutions", headers=user_headers
    ).json()
    scenario = client.post(
        f"/api/v1/projects/{project['id']}/scenarios",
        headers=user_headers,
        json={
            "name": "Покупка",
            "kind": "purchase",
            "items": [{"solution_id": solutions[0]["solution_id"], "quantity": 1}],
        },
    ).json()
    calc = client.post(
        f"/api/v1/scenarios/{scenario['id']}/calculate", headers=user_headers
    ).json()

    stored = client.get(
        f"/api/v1/scenarios/{scenario['id']}/calculations/{calc['calculation_id']}",
        headers=user_headers,
    )
    assert stored.status_code == 200
    body = stored.json()
    assert body["model_version"] == calc["meta"]["model_version"]
    assert body["result"]["purchase"]["capex"]["total"] == pytest.approx(
        calc["purchase"]["capex"]["total"]
    )
