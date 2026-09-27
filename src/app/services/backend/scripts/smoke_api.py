#!/usr/bin/env python
"""Живой прогон API: поднимает TestClient и проходит основной пользовательский путь.

Проверяется не «эндпоинт вернул 200», а что данные осмысленны: подбор находит
подходящие решения, расчёт выдаёт окупаемость, чужой проект недоступен.
"""

from __future__ import annotations

import json
import sys

from fastapi.testclient import TestClient

BASE = "http://testserver"


def show(title: str, value) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(value, ensure_ascii=False, indent=2)[:1400])


def main() -> int:
    from app.main import app

    client = TestClient(app)
    failures: list[str] = []

    def check(cond: bool, message: str) -> None:
        print(("  ok   " if cond else "  FAIL ") + message)
        if not cond:
            failures.append(message)

    # ── Гость ─────────────────────────────────────────────────────────────
    print("ГОСТЬ")
    r = client.get("/api/v1/object-types")
    check(r.status_code == 200, "справочник типов объектов открыт гостю")
    types = r.json()
    check(len(types) == 3, f"три типа объекта (получено {len(types)})")
    for t in types:
        print(f"    {t['code']:10s} {t['name']:32s} процессов {t['process_count']:2d}, "
              f"параметров {t['parameter_count']:3d}")

    r = client.get("/api/v1/catalog", params={"limit": 3, "sort": "price", "desc": True})
    check(r.status_code == 200, "каталог открыт гостю")
    cat = r.json()
    # По умолчанию показываются решения, а не комплектации: 226 строк каталога
    # включают 36 вариантов одного и того же изделия.
    check(cat["total"] == 190, f"в каталоге {cat['total']} решений (без вариантов)")
    r = client.get("/api/v1/catalog", params={"include_variants": True, "limit": 1})
    check(r.json()["total"] == 226, f"с вариантами комплектаций {r.json()['total']}")
    check(bool(cat["facets"]), "фасеты фильтров заполнены")
    for f in ("status", "solution_type", "vendor", "price_source", "object_type"):
        check(f in cat["facets"] and len(cat["facets"][f]) > 0, f"фасет «{f}» непуст")
    for item in cat["items"][:2]:
        print(f"    {item['name'][:48]:48s} {item['unit_price_rub'] or 0:>12,.0f} руб "
              f"[{item['price_source']}]")

    r = client.get("/api/v1/projects")
    check(r.status_code == 401, "проекты гостю недоступны (401)")
    check(r.json().get("code") == "unauthorized", "ошибка 401 в формате ТЗ 4.5.4")
    check("hint" in r.json(), "в ошибке есть подсказка как исправить")

    # ── Регистрация и вход ────────────────────────────────────────────────
    print("\nПОЛЬЗОВАТЕЛЬ")
    email = "api-test@example.com"
    client.post("/api/v1/auth/register",
                json={"email": email, "password": "test12345", "full_name": "Тест"})
    r = client.post("/api/v1/auth/login", json={"email": email, "password": "test12345"})
    check(r.status_code == 200, "вход выполнен")
    tokens = r.json()
    auth = {"Authorization": f"Bearer {tokens['access_token']}"}
    check(tokens["user"]["role"] == "user", "роль нового пользователя — user")

    r = client.post("/api/v1/auth/login", json={"email": email, "password": "неверный"})
    check(r.status_code == 401, "неверный пароль отклонён")
    check("Неверная почта или пароль" in r.json()["message"],
          "сообщение не раскрывает, существует ли такой e-mail")

    r = client.post("/api/v1/auth/register",
                    json={"email": email, "password": "test12345"})
    check(r.status_code == 409, "повторная регистрация e-mail отклонена (409)")

    # ── Проект ────────────────────────────────────────────────────────────
    defaults = client.get("/api/v1/object-types/warehouse/parameters/defaults").json()
    params = {k: v for k, v in defaults["values"].items() if v is not None}
    procs = [p["code"] for p in
             client.get("/api/v1/processes", params={"object_type": "warehouse"}).json()]
    check(len(procs) > 0, f"процессы склада: {len(procs)}")
    print("    " + ", ".join(procs))

    r = client.post("/api/v1/projects", headers=auth, json={
        "name": "Склад — прогон API", "object_type": "warehouse",
        "parameters": params, "process_codes": ["intra_logistics"],
    })
    check(r.status_code == 201, "проект создан")
    project = r.json()
    print(f"    id={project['id']} статус={project['status']} "
          f"параметров={len(project['parameters'])}")

    r = client.post("/api/v1/projects", headers=auth, json={
        "name": "Ошибка", "object_type": "warehouse",
        "parameters": {"не_существует": 1},
    })
    check(r.status_code == 400 and r.json()["code"] == "unknown_parameters",
          "неизвестный параметр отклонён, а не проигнорирован")

    r = client.post("/api/v1/projects", headers=auth, json={
        "name": "Ошибка", "object_type": "warehouse",
        "process_codes": ["не_существует"],
    })
    check(r.status_code == 400 and r.json()["code"] == "unknown_processes",
          "чужой процесс отклонён")

    # ── Подбор ────────────────────────────────────────────────────────────
    print("\nПОДБОР")
    r = client.post("/api/v1/match", headers=auth, json={
        "object_type": "warehouse", "process_code": "intra_logistics",
        "parameters": params, "limit": 5,
    })
    check(r.status_code == 200, "подбор выполнен")
    match = r.json()
    print(f"    требований {len(match['requirements'])}, пиковая потребность "
          f"{match['peak_demand']} {match['demand_unit']}, "
          f"рассмотрено {match['summary']['considered']}, "
          f"подходящих {match['summary']['eligible']}")
    check(match["summary"]["eligible"] > 0, "есть подходящие решения")
    for res in match["results"][:5]:
        flag = "+" if res["is_eligible"] else "-"
        print(f"    {flag} {res['score']:5.1f}  {res['name'][:44]:44s} "
              f"{(res['vendor'] or '—')[:22]:22s} {res['unit_price_rub'] or 0:>11,.0f} руб")
        for c in res["checks"]:
            if not c["passed"]:
                print(f"        ✗ {c['message']}")

    r = client.get("/api/v1/requirements", params={
        "object_type": "warehouse", "process_code": "intra_logistics",
    })
    check(r.status_code == 200 and len(r.json()["requirements"]) > 0,
          "требования отдаются и без подбора")

    # ── Сохранение подбора и расчёт ───────────────────────────────────────
    r = client.post(f"/api/v1/projects/{project['id']}/match?limit=3", headers=auth)
    check(r.status_code == 200, "подбор сохранён в проект")
    added = r.json()["added"]
    check(len(added) > 0, f"в подборку добавлено решений: {len(added)}")
    for a in added[:5]:
        print(f"    {a['score']:5.1f}  {a['name'][:52]}")

    r = client.get(f"/api/v1/projects/{project['id']}/solutions", headers=auth)
    sol_ids = [s["solution_id"] for s in r.json()]

    r = client.post(f"/api/v1/projects/{project['id']}/scenarios", headers=auth, json={
        "name": "Покупка", "kind": "purchase",
        "items": [{"solution_id": sid, "quantity": 4} for sid in sol_ids[:3]],
        "horizon_years": 5,
    })
    check(r.status_code == 201, "сценарий покупки создан")
    scenario = r.json()

    r = client.post(f"/api/v1/scenarios/{scenario['id']}/calculate", headers=auth)
    check(r.status_code == 200, "расчёт выполнен")
    calc = r.json()
    show("мета", calc["meta"])
    for kind in ("baseline", "purchase", "raas"):
        s = calc[kind]
        if not s:
            continue
        capex = s["capex"]["total"]
        opex = s["opex"]["total"]
        print(f"  {kind:9s} CAPEX {capex:>14,.0f} | OPEX/год {opex:>12,.0f} | "
              f"эффект/год {(s['effect'].get('net_annual_cash') or 0):>12,.0f} | "
              f"остаточный ФОТ {(s.get('residual_labor_annual') or 0):>13,.0f} | "
              f"окупаемость {s['payback_years']}")
    check(calc["purchase"]["payback_years"] is not None, "окупаемость посчитана")
    check(calc["tco"]["best_option"] in ("baseline", "purchase", "raas"),
          f"выбран лучший вариант: {calc['tco']['best_option']}")
    print("  TCO:")
    for k, v in calc["tco"]["scenarios"].items():
        print(f"    {k:9s} {v['total']:>15,.0f} руб за {calc['tco']['horizon_years']} лет")
    check(len(calc["sensitivity"]) > 0, "анализ чувствительности выполнен")
    for block in calc["sensitivity"]:
        ys = [p["payback_years"] for p in block["points"]]
        print(f"    {block['label']}: окупаемость {min(ys)}…{max(ys)} лет")
    if calc["warnings"]:
        print("  предупреждения:")
        for w in calc["warnings"]:
            print(f"    - {w}")

    # ── RaaS-эффект не должен быть отрицательным там, где проект окупается ──
    p = calc["purchase"]
    if p["payback_years"]:
        check(p["effect"]["net_annual_cash"] > 0,
              "денежный эффект положителен при конечной окупаемости")

    # ── Имитация ──────────────────────────────────────────────────────────
    print("\nИМИТАЦИЯ")
    r = client.post(f"/api/v1/scenarios/{scenario['id']}/simulate", headers=auth,
                    json={"seed": 42, "include_schedule": True})
    check(r.status_code == 201, "имитация выполнена")
    sim = r.json()
    kpi = sim["kpi"]
    print(f"    роботов {kpi['robots']}, зон {kpi['zones']}, "
          f"станций {kpi['charging_stations']}, задач {kpi['tasks_total']}, "
          f"загрузка {kpi['utilization_pct']}%, seed {kpi['seed']}")
    print(f"    полотно {sim['layout']['width_m']}×{sim['layout']['depth_m']} м, "
          f"маршрутов {len(sim['layout']['routes'])}")
    if kpi.get("bottleneck"):
        print(f"    узкое место: {kpi['bottleneck']['name']}")
    check(sim["layout"]["robots"] and sim["layout"]["zones"],
          "раскладка содержит роботов и зоны")
    check(sim["schedule"] and sim["schedule"]["by_robot"],
          "расписание задач построено")

    # детерминированность: тот же seed — тот же результат
    r2 = client.post(f"/api/v1/scenarios/{scenario['id']}/simulate", headers=auth,
                     json={"seed": 42, "include_schedule": True, "persist": False})
    check(r2.json()["layout"] == sim["layout"],
          "повторный запуск с тем же seed даёт ту же раскладку")

    # ── Доступ к чужому проекту ───────────────────────────────────────────
    print("\nРАЗГРАНИЧЕНИЕ ДОСТУПА")
    r = client.post("/api/v1/auth/register", json={
        "email": "api-other@example.com", "password": "test12345"})
    if r.status_code != 201:
        # учётка осталась с прошлого прогона — входим, а не падаем
        r = client.post("/api/v1/auth/login", json={
            "email": "api-other@example.com", "password": "test12345"})
    check(r.status_code == 200, "второй пользователь создан")
    other = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.get(f"/api/v1/projects/{project['id']}", headers=other)
    check(r.status_code == 403, "чужой проект недоступен (403)")
    r = client.get(f"/api/v1/scenarios/{scenario['id']}/calculate", headers=other)
    check(r.status_code == 403, "чужой сценарий недоступен (403)")
    r = client.get(f"/api/v1/scenarios/{scenario['id']}/calculations/1", headers=other)
    check(r.status_code == 403, "чужой расчёт недоступен (403)")
    r = client.get(f"/api/v1/admin/stats", headers=other)
    check(r.status_code == 403, "админские методы закрыты обычному пользователю")

    # ── Администратор ─────────────────────────────────────────────────────
    print("\nАДМИНИСТРАТОР")
    r = client.post("/api/v1/auth/login",
                    json={"email": "admin@example.com", "password": "demo12345"})
    check(r.status_code == 200, "демо-администратор вошёл")
    admin = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r = client.get("/api/v1/admin/stats", headers=admin)
    check(r.status_code == 200, "сводка платформы доступна")
    print("    " + json.dumps(r.json(), ensure_ascii=False))

    norms = client.get("/api/v1/normatives", headers=admin).json()
    editable = [n for n in norms if n["is_editable"]]
    target = next(n for n in editable if n["min_value"] is not None)
    r = client.patch(f"/api/v1/admin/normatives/{target['id']}", headers=admin,
                     json={"value": target["min_value"]})
    check(r.status_code == 200, f"норматив «{target['name']}» изменён")
    r = client.patch(f"/api/v1/admin/normatives/{target['id']}", headers=admin,
                     json={"value": float(target["min_value"]) * 1000})
    check(r.status_code == 400 and r.json()["code"] == "out_of_range",
          "выход за диапазон отклонён")
    client.patch(f"/api/v1/admin/normatives/{target['id']}", headers=admin,
                 json={"value": target["value"]})
    r = client.get("/api/v1/admin/audit?limit=3", headers=admin)
    check(r.status_code == 200 and len(r.json()) > 0, "журнал аудита ведётся")
    print(f"    последнее действие: {r.json()[0]['action']} {r.json()[0]['entity']}")

    # ── Допущения ─────────────────────────────────────────────────────────
    r = client.get("/api/v1/assumptions")
    check(r.status_code == 200, "допущения расчёта открыты")
    a = r.json()
    check(a["count"] > 30, f"нормативов в модели: {a['count']}")
    overridable = [x for x in a["assumptions"] if x["overridable_by_user"]]
    print(f"    из них пользователь может переопределить: {len(overridable)}")
    for x in overridable[:6]:
        print(f"      {x['code']:34s} = {x['value']:>12} диапазон {x['range']}")

    r = client.post(f"/api/v1/projects/{project['id']}/scenarios", headers=auth, json={
        "name": "С плохим допущением", "kind": "purchase",
        "items": [{"solution_id": sol_ids[0], "quantity": 2}],
        "assumptions": {" payroll.multiplier ": 99},
    })
    check(r.status_code == 400 and r.json()["code"] == "unknown_assumptions",
          "неизвестное допущение отклонено")

    print("\n" + "=" * 62)
    if failures:
        print(f"ПРОВАЛЕНО {len(failures)}:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("Все проверки пройдены.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
