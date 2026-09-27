"""PDF-отчёт по расчёту: воспроизводимый снимок для жюри и заказчика.

Отчёт строится из сохранённого снимка расчёта (`Calculation.result`), а не
пересчитывается заново. Это принципиально: через неделю после расчёта
нормативы или каталог могут измениться, и пересчёт показал бы другие цифры,
чем те, что видел пользователь на экране. ТЗ 3.1.5 требует воспроизводимости —
отчёт обязан показывать ровно то, что было посчитано.

Кириллица: reportlab сам по себе знает только латиницу, поэтому шрифты
DejaVu регистрируются явно из app/assets. Без этого весь русский текст
превращается в чёрные прямоугольники — молча и только в готовом файле.
"""

from __future__ import annotations

import io
from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# backend/app/services/reports/pdf.py → backend/app/assets
ASSETS = Path(__file__).resolve().parents[2] / "assets"

_FONT_REGISTERED = False


def _register_fonts() -> None:
    """Регистрирует DejaVu для кириллицы. Один раз на процесс."""
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return
    pdfmetrics.registerFont(TTFont("DejaVu", str(ASSETS / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Bold", str(ASSETS / "DejaVuSans-Bold.ttf")))
    pdfmetrics.registerFont(TTFont("DejaVu-Italic", str(ASSETS / "DejaVuSans-Oblique.ttf")))
    pdfmetrics.registerFontFamily(
        "DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu-Italic"
    )
    _FONT_REGISTERED = True


# ─────────────────────────────────────────────────────────────────────────────
# Форматирование
# ─────────────────────────────────────────────────────────────────────────────


def _money(value: Any) -> str:
    """12 345 678 ₽ — с разделителями и без копеек."""
    if value is None:
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)
    return f"{number:,.0f} ₽".replace(",", " ")


def _num(value: Any, digits: int = 2) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):,.{digits}f}".replace(",", " ")
    except (TypeError, ValueError):
        return str(value)


def _pct(value: Any) -> str:
    if value is None:
        return "—"
    try:
        return f"{float(value):.1f} %"
    except (TypeError, ValueError):
        return str(value)


def _yes_no(value: Any) -> str:
    if value is None:
        return "не указано"
    return "да" if value else "нет"


def _text(value: Any) -> str:
    if value is None or value == "":
        return "—"
    return str(value).replace("\n", " ")


# ─────────────────────────────────────────────────────────────────────────────
# Стили
# ─────────────────────────────────────────────────────────────────────────────


def _styles() -> dict[str, ParagraphStyle]:
    base = getSampleStyleSheet()
    styles: dict[str, ParagraphStyle] = {
        "title": ParagraphStyle(
            "title", parent=base["Title"], fontName="DejaVu-Bold", fontSize=17,
            leading=21, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "subtitle", parent=base["Normal"], fontName="DejaVu", fontSize=10,
            leading=14, textColor=colors.HexColor("#444444"),
        ),
        "h2": ParagraphStyle(
            "h2", parent=base["Heading2"], fontName="DejaVu-Bold", fontSize=12.5,
            leading=16, spaceBefore=14, spaceAfter=5,
            textColor=colors.HexColor("#1a3a5c"),
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"], fontName="DejaVu", fontSize=9.5,
            leading=13.5, spaceAfter=4,
        ),
        "small": ParagraphStyle(
            "small", parent=base["Normal"], fontName="DejaVu", fontSize=8,
            leading=11, textColor=colors.HexColor("#555555"),
        ),
        "cell": ParagraphStyle(
            "cell", parent=base["Normal"], fontName="DejaVu", fontSize=8.2,
            leading=11,
        ),
        "cell_bold": ParagraphStyle(
            "cell_bold", parent=base["Normal"], fontName="DejaVu-Bold", fontSize=8.2,
            leading=11,
        ),
        "cell_head": ParagraphStyle(
            "cell_head", parent=base["Normal"], fontName="DejaVu-Bold", fontSize=8.2,
            leading=11, textColor=colors.white,
        ),
        "note": ParagraphStyle(
            "note", parent=base["Normal"], fontName="DejaVu-Italic", fontSize=8.5,
            leading=12, textColor=colors.HexColor("#555555"), spaceAfter=4,
        ),
    }
    return styles


def _table(headers: list[str], rows: list[list[Any]], widths: list[float]) -> Table:
    """Таблица с шапкой и переносом длинных строк."""
    styles = _styles()
    data: list[list[Any]] = [
        [Paragraph(h, styles["cell_head"]) for h in headers]
    ]
    for row in rows:
        data.append([Paragraph(_text(cell), styles["cell"]) for cell in row])
    table = Table(data, colWidths=widths, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a3a5c")),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4d0")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f5f8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


def _kv_table(pairs: list[tuple[str, Any]], widths: list[float]) -> Table:
    """Двухколонная таблица «показатель — значение»."""
    styles = _styles()
    data = [
        [Paragraph(_text(k), styles["cell"]), Paragraph(_text(v), styles["cell_bold"])]
        for k, v in pairs
    ]
    table = Table(data, colWidths=widths)
    table.setStyle(
        TableStyle(
            [
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#b8c4d0")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#eef2f6")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]
        )
    )
    return table


# ─────────────────────────────────────────────────────────────────────────────
# Разделы
# ─────────────────────────────────────────────────────────────────────────────


def _header(calc: Any, result: dict[str, Any]) -> list[Any]:
    """Титульный блок: что за проект, кем и когда посчитано, на каких данных."""
    styles = _styles()
    meta = result.get("meta") or {}
    project = calc.scenario.project if calc.scenario else None
    scenario = calc.scenario

    story: list[Any] = [
        Paragraph("Расчёт экономического эффекта роботизации", styles["title"]),
        Paragraph(
            f"{project.name if project else '—'} · {scenario.name if scenario else '—'}",
            styles["subtitle"],
        ),
        Spacer(1, 4),
        HRFlowable(width="100%", thickness=1, color=colors.HexColor("#1a3a5c")),
        Spacer(1, 8),
    ]

    pairs: list[tuple[str, Any]] = [
        ("Тип объекта", meta.get("object_type_name") or "—"),
        ("Проект", project.name if project else "—"),
        ("Организация", project.organization if project and project.organization else "—"),
        ("Сценарий", scenario.name if scenario else "—"),
        (
            "Процессы",
            ", ".join(meta.get("process_codes") or []) or "—",
        ),
        ("Горизонт расчёта", f"{meta.get('horizon_years', '—')} лет"),
        ("Версия расчётной модели", meta.get("model_version") or "—"),
        ("Версия каталога решений", meta.get("catalog_version") or "—"),
        ("Дата расчёта", (calc.computed_at or datetime.now()).strftime("%d.%m.%Y %H:%M")),
    ]
    story.append(_kv_table(pairs, [55 * mm, 115 * mm]))
    return story


def _solutions(result: dict[str, Any]) -> list[Any]:
    """Подбор решения: позиции с количеством, ценой и источником цены."""
    styles = _styles()
    purchase = result.get("purchase") or {}
    equipment = purchase.get("equipment") or []
    if not equipment:
        return []

    story: list[Any] = [Paragraph("1. Состав оборудования", styles["h2"])]
    rows = []
    for line in equipment:
        sizing = line.get("sizing") or {}
        rows.append(
            [
                _text(line.get("name")),
                _text(line.get("vendor")),
                line.get("quantity"),
                _money(line.get("unit_price")),
                _text(line.get("price_source")),
                _text(sizing.get("formula")) if sizing else "количество задано вручную",
            ]
        )
    story.append(
        _table(
            ["Решение", "Поставщик", "Кол-во", "Цена", "Источник цены", "Обоснование количества"],
            rows,
            [42 * mm, 30 * mm, 12 * mm, 24 * mm, 20 * mm, 42 * mm],
        )
    )
    story.append(
        Paragraph(
            "Источник цены: «каталог» — цена из файла организатора, "
            "«запрос поставщика» — подтверждённая котировка, "
            "«оценка» — расчётная оценка платформы.",
            styles["note"],
        )
    )
    return story


def _scenario_block(title: str, scenario: dict[str, Any]) -> list[Any]:
    """CAPEX, OPEX, эффект и окупаемость одного сценария."""
    styles = _styles()
    capex = scenario.get("capex") or {}
    opex = scenario.get("opex") or {}
    effect = scenario.get("effect") or {}
    payback = scenario.get("payback") or {}

    story: list[Any] = [Paragraph(title, styles["h2"])]

    story.append(
        _kv_table(
            [
                ("CAPEX, всего", _money(capex.get("total"))),
                ("OPEX, в год", _money(opex.get("total"))),
                ("Экономия ФОТ в год", _money(effect.get("labor_saving"))),
                ("Прочий эффект в год", _money(
                    (effect.get("quality") or 0)
                    + (effect.get("throughput") or 0)
                    + (effect.get("safety") or 0)
                )),
                ("Годовой эффект (денежный поток)", _money(effect.get("net_annual_cash"))),
                ("Годовой эффект (с амортизацией, ТЗ 3.5.4)", _money(effect.get("net_annual"))),
                ("Окупаемость", _num(payback.get("cash_payback_years")) + " лет"
                 if payback.get("cash_payback_years") else "не окупается в горизонте"),
                ("ROI", _pct(scenario.get("roi_pct"))),
                ("Остаточный ФОТ в год", _money(scenario.get("residual_labor_annual"))),
            ],
            [70 * mm, 100 * mm],
        )
    )

    # Структура затрат — только если есть ненулевые статьи
    capex_rows = [
        (name, value)
        for name, value in [
            ("Оборудование", capex.get("equipment")),
            ("Программное обеспечение", capex.get("software")),
            ("Интеграция", capex.get("integration")),
            ("Пусконаладка", capex.get("commissioning")),
            ("Обучение персонала", capex.get("training")),
            ("Зарядная инфраструктура", capex.get("charging_stations")),
            ("Резерв на непредвиденные работы", capex.get("reserve")),
        ]
        if value
    ]
    if capex_rows:
        story.append(Paragraph("Структура капитальных затрат", styles["body"]))
        story.append(
            _kv_table(
                [(name, _money(value)) for name, value in capex_rows],
                [110 * mm, 60 * mm],
            )
        )

    opex_rows = [
        (name, value)
        for name, value in [
            ("Техническое обслуживание", opex.get("service")),
            ("Лицензии на ПО", opex.get("licenses")),
            ("Электроэнергия", opex.get("energy")),
            ("Расходные материалы", opex.get("consumables")),
            ("Сопровождение интеграции", opex.get("integration_support")),
            ("Страхование", opex.get("insurance")),
            ("Замена аккумуляторов", opex.get("battery_replacement")),
        ]
        if value
    ]
    if opex_rows:
        story.append(Paragraph("Структура операционных затрат, в год", styles["body"]))
        story.append(
            _kv_table(
                [(name, _money(value)) for name, value in opex_rows],
                [110 * mm, 60 * mm],
            )
        )
    return story


def _schedule(scenario: dict[str, Any]) -> list[Any]:
    """Динамика по годам: накопленный денежный поток и эффект."""
    styles = _styles()
    rows = scenario.get("schedule") or []
    if not rows:
        return []
    story: list[Any] = [Paragraph("Динамика по годам", styles["body"])]
    story.append(
        _table(
            [
                "Год",
                "Экономия ФОТ",
                "OPEX",
                "Амортизация",
                "Эффект (деньги)",
                "Накопленный поток",
                "ROI",
            ],
            [
                [
                    r.get("year"),
                    _money(r.get("labor_saving")),
                    _money(r.get("opex")),
                    _money(r.get("amortization")),
                    _money(r.get("net_annual_cash")),
                    _money(r.get("cumulative_cash")),
                    _pct(r.get("roi_pct")),
                ]
                for r in rows
            ],
            [14 * mm, 28 * mm, 26 * mm, 24 * mm, 30 * mm, 30 * mm, 18 * mm],
        )
    )
    return story


def _tco(result: dict[str, Any]) -> list[Any]:
    """Сравнение сценариев по совокупной стоимости владения."""
    styles = _styles()
    tco = result.get("tco") or {}
    scenarios = tco.get("scenarios") or {}
    if not scenarios:
        return []
    story: list[Any] = [Paragraph("2. Сравнение сценариев (TCO)", styles["h2"])]
    labels = {"baseline": "Без роботизации", "purchase": "Покупка", "raas": "RaaS"}
    rows = []
    for key in ("baseline", "purchase", "raas"):
        block = scenarios.get(key) or {}
        rows.append(
            [
                labels.get(key, key),
                _money(block.get("setup")),
                _money(block.get("annual")),
                _money(block.get("residual_labor_annual")),
                _money(block.get("total")),
            ]
        )
    story.append(
        _table(
            ["Сценарий", "Единовременно", "В год", "Остаточный ФОТ в год", "TCO за горизонт"],
            rows,
            [34 * mm, 34 * mm, 30 * mm, 40 * mm, 32 * mm],
        )
    )
    best = tco.get("best_option")
    if best:
        story.append(
            Paragraph(
                f"Наименьшая совокупная стоимость владения: "
                f"{labels.get(best, best).lower()}. "
                f"{_text(tco.get('note'))}",
                styles["note"],
            )
        )
    return story


def _sensitivity(result: dict[str, Any]) -> list[Any]:
    """Анализ чувствительности: как меняется окупаемость при отклонении параметров."""
    styles = _styles()
    sens = result.get("sensitivity") or []
    if not sens:
        return []
    story: list[Any] = [Paragraph("3. Анализ чувствительности", styles["h2"])]
    story.append(
        Paragraph(
            "Окупаемость при отклонении параметра от базового значения. "
            "Точка 1,0 — базовый расчёт.",
            styles["note"],
        )
    )
    for block in sens:
        rows = []
        for point in block.get("points") or []:
            rows.append(
                [
                    f"{point.get('factor', 0):.2f}×",
                    _money(point.get("capex")),
                    _money(point.get("annual_effect")),
                    (
                        _num(point.get("payback_years")) + " лет"
                        if point.get("payback_years")
                        else "не окупается"
                    ),
                ]
            )
        story.append(Paragraph(_text(block.get("label")), styles["body"]))
        story.append(
            _table(
                ["Отклонение", "CAPEX", "Эффект в год", "Окупаемость"],
                rows,
                [30 * mm, 48 * mm, 48 * mm, 44 * mm],
            )
        )
    return story


def _assumptions(result: dict[str, Any]) -> list[Any]:
    """Допущения расчёта: значение и источник каждого коэффициента."""
    styles = _styles()
    rows = []
    for a in result.get("assumptions") or []:
        rows.append(
            [
                _text(a.get("code")),
                _text(a.get("value")),
                _text(a.get("source")),
                "да" if a.get("is_override") else "нет",
            ]
        )
    if not rows:
        return []
    story: list[Any] = [Paragraph("4. Допущения расчёта", styles["h2"])]
    story.append(
        _table(
            ["Код", "Значение", "Источник", "Изменено пользователем"],
            rows,
            [52 * mm, 26 * mm, 72 * mm, 20 * mm],
        )
    )
    return story


def _warnings(result: dict[str, Any]) -> list[Any]:
    styles = _styles()
    warnings = result.get("warnings") or []
    if not warnings:
        return []
    story: list[Any] = [Paragraph("5. Ограничения расчёта", styles["h2"])]
    for w in warnings:
        story.append(Paragraph(f"• {_text(w)}", styles["body"]))
    return story


def _footer(calc: Any) -> list[Any]:
    styles = _styles()
    return [
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#b8c4d0")),
        Spacer(1, 4),
        Paragraph(
            "Отчёт сформирован платформой подбора роботизированных решений. "
            "Все коэффициенты хранятся в справочнике нормативов и доступны "
            "администратору для правки; расчёт воспроизводится по снимку, "
            "включая версии каталога и модели.",
            styles["small"],
        ),
    ]


# ─────────────────────────────────────────────────────────────────────────────
# Сборка
# ─────────────────────────────────────────────────────────────────────────────


def build_report(calc: Any) -> bytes:
    """PDF-отчёт по снимку расчёта.

    Принимает объект `Calculation`, а не идентификатор: отчёт читает сохранённый
    снимок и не зависит от того, что сейчас лежит в каталоге и нормативах.
    """
    _register_fonts()
    result = calc.result or {}
    if not isinstance(result, dict):
        raise ValueError("В снимке расчёта нет результата")

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Расчёт экономического эффекта роботизации",
        author="Платформа подбора роботизированных решений",
    )

    story: list[Any] = []
    story.extend(_header(calc, result))
    story.extend(_solutions(result))

    purchase = result.get("purchase") or {}
    raas = result.get("raas") or {}
    if purchase:
        story.extend(_scenario_block("Сценарий «Покупка оборудования»", purchase))
        story.extend(_schedule(purchase))
    if raas:
        story.extend(_scenario_block("Сценарий «Роботы как услуга» (RaaS)", raas))
        story.extend(_schedule(raas))

    story.extend(_tco(result))
    story.extend(_sensitivity(result))
    story.extend(_assumptions(result))
    story.extend(_warnings(result))
    story.extend(_footer(calc))

    doc.build(story)
    return buffer.getvalue()
