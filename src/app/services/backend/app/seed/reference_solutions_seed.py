"""Эталонные решения с подтверждёнными ТТХ (документ организатора).

Файл «Примеры решений типы объектов.docx» содержит ТТХ восьми конкретных
изделий — по одному-два на каждый тип решения для каждого из трёх объектов.
Это единственный источник с числовыми ТТХ, поэтому именно эти позиции
показываются в витрине как «данные подтверждены», а расчёт по ним даёт
воспроизводимый результат.

Там, где изделие присутствует и в каталоге организатора, цена берётся из
каталога; там, где его нет (шаттл Stelcon, тягач Cognitive Pilot,
PuduBot 2), цена — явное оценочное допущение, помеченное price_source =
«estimate», чтобы расчёт работал, а его точность не выдавалась за факт.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class ReferenceSolution:
    slug: str
    name: str
    vendor: str
    solution_type: str
    object_types: tuple[str, ...]
    process_codes: tuple[str, ...]
    specs: dict[str, object]
    source_name: str
    source_url: str
    #: подстрока названия в каталоге организатора для забора цены и статуса
    catalog_match: str | None = None
    note: str | None = None
    restrictions: tuple[str, ...] = field(default=())


def _m(length_mm: float, width_mm: float, height_mm: float) -> dict[str, Decimal]:
    return {
        "length_m": Decimal(str(length_mm / 1000)).quantize(Decimal("0.001")),
        "width_m": Decimal(str(width_mm / 1000)).quantize(Decimal("0.001")),
        "height_m": Decimal(str(height_mm / 1000)).quantize(Decimal("0.001")),
    }


# Ширина проезда выводится из габаритов корпуса: ширина + запас на разминовку.
# Проверку «пройдёт ли робот» платформа делает по этому полю.
def _passage(width_mm: float, margin_mm: float = 300) -> Decimal:
    return Decimal(str((width_mm + margin_mm) / 1000)).quantize(Decimal("0.001"))


WAREHOUSE_AMR = ReferenceSolution(
    slug="ronavi-h1500",
    name="Ronavi H1500",
    vendor="ООО «Ронави Роботикс»",
    solution_type="amr",
    object_types=("warehouse", "airport"),
    process_codes=("intra_logistics", "receiving", "shipping", "storage"),
    specs={
        "payload_kg": Decimal("1500"),
        "own_weight_kg": Decimal("250"),
        **_m(1044, 654, 380),
        "min_passage_width_m": _passage(654),
        "max_speed_mps": Decimal("1.5"),
        "charge_time_min": Decimal("18"),
        "autonomy_hours": Decimal("6"),
        "throughput_per_hour": Decimal("80"),
        "throughput_unit": "паллет/ч",
        "positioning_accuracy_mm": Decimal("3"),
        "navigation_types": ["QR-метки", "SLAM (карта помещения)"],
        "min_temp_c": Decimal("5"),
        "max_temp_c": Decimal("25"),
        "max_floor_roughness_mm": Decimal("3"),
        "lifetime_years": Decimal("7"),
        "battery_lifetime_years": Decimal("4"),
    },
    source_name="Примеры решений организатора → роботизация склада → AMR",
    source_url="https://ronavi-robotics.ru/catalogue/h1500",
    catalog_match="Ronavi H1500",
    note="Типовая производительность 80–100 паллет/ч принята как 80 (пессимистично).",
)

WAREHOUSE_FMR = ReferenceSolution(
    slug="dmr-carrier-p",
    name="DMR Carrier P",
    vendor="ООО «Диком-Сервис»",
    solution_type="fmr",
    object_types=("warehouse",),
    process_codes=("storage", "intra_logistics", "shipping", "picking"),
    specs={
        "payload_kg": Decimal("1500"),
        "own_weight_kg": Decimal("2250"),
        # в источнике приведён порядок В×Ш×Г
        **_m(1000, 1975, 2050),
        "min_passage_width_m": _passage(1975, 400),
        "lift_height_m": Decimal("1.6"),
        "max_speed_mps": Decimal("1.5"),
        "autonomy_hours": Decimal("10"),
        "throughput_per_hour": Decimal("40"),
        "throughput_unit": "паллет/ч",
        "navigation_types": ["SLAM на базе лидаров"],
        "min_temp_c": Decimal("5"),
        "max_temp_c": Decimal("35"),
        "lifetime_years": Decimal("8"),
        "battery_lifetime_years": Decimal("4"),
    },
    source_name="Примеры решений организатора → роботизация склада → FMR",
    source_url="https://tnvst.ru/catalog/fmr-roboty/avtonomnyy-mobilnyy-robot-dikom-dmr-carrier-p",
    catalog_match="DMR Carrier P",
    note="Масса 2000–2500 кг принята как 2250 кг; производительность 40–60 паллет/ч принята как 40.",
    restrictions=("Требуется ровное бетонное покрытие пола",),
)

CLEANER_MARK2 = ReferenceSolution(
    slug="mark-2-se",
    name="MARK 2 SE",
    vendor="ООО «Р2Б»",
    solution_type="cleaner",
    object_types=("warehouse", "airport", "medical"),
    process_codes=("cleaning", "ground_cleaning"),
    specs={
        "own_weight_kg": Decimal("165"),
        **_m(860, 610, 980),
        "min_passage_width_m": _passage(610, 200),
        # 3–4 км/ч
        "max_speed_mps": Decimal("1.1"),
        "autonomy_hours": Decimal("3"),
        "charge_time_min": Decimal("120"),
        "throughput_per_hour": Decimal("1000"),
        "throughput_unit": "м²/ч",
        "navigation_types": ["лидар", "камеры", "построение карты и маршрутов"],
        "min_temp_c": Decimal("0"),
        "max_temp_c": Decimal("40"),
        "lifetime_years": Decimal("7"),
        "battery_lifetime_years": Decimal("4"),
    },
    source_name="Примеры решений организатора → робот-уборщик помещений",
    source_url="https://r2b.company/mark2se",
    catalog_match="MARK 2 SE",
    note="Время работы 3 ч (до 4 ч со станцией); масса 130–200 кг принята как 165 кг.",
)

SHUTTLE_STELCON = ReferenceSolution(
    slug="stelcon-pallet-shuttle",
    name="Pallet Shuttle",
    vendor="Stelcon",
    solution_type="shuttle",
    object_types=("warehouse",),
    process_codes=("storage", "picking"),
    specs={
        "payload_kg": Decimal("1500"),
        **_m(1200, 800, 200),
        "max_speed_mps": Decimal("1.0"),
        "autonomy_hours": Decimal("8"),
        "throughput_per_hour": Decimal("80"),
        "throughput_unit": "паллет/ч на канал",
        "navigation_types": ["рейки в канальных стеллажах"],
        "lifetime_years": Decimal("15"),
        "battery_lifetime_years": Decimal("4"),
    },
    source_name="Примеры решений организатора → шаттл-система",
    source_url="https://www.stelkon.ru/catalog/palletnye-stellazhi/pallet/",
    catalog_match=None,
    note=(
        "Высота склада до 12–15 м; в каталоге организатора позиция отсутствует, "
        "цена — оценочное допущение."
    ),
    restrictions=("Требует проектирования стеллажей и каналов под систему",),
)

TUGGER_COGNITIVE = ReferenceSolution(
    slug="cognitive-pilot-tugger",
    name="Cognitive Pilot (беспилотный тягач)",
    vendor="Cognitive Pilot",
    solution_type="tugger",
    object_types=("airport",),
    process_codes=("ground_handling", "terminal_logistics", "baggage"),
    specs={
        "payload_kg": Decimal("3000"),
        "own_weight_kg": Decimal("1250"),
        **_m(2300, 1400, 1500),
        "min_passage_width_m": _passage(1400),
        # рабочая скорость 5–25 км/ч
        "max_speed_mps": Decimal("7"),
        "autonomy_hours": Decimal("24"),
        "navigation_types": ["камеры", "лидары", "радары", "нейросетевой автопилот"],
        "min_temp_c": Decimal("-30"),
        "max_temp_c": Decimal("45"),
        "lifetime_years": Decimal("10"),
        "battery_lifetime_years": Decimal("5"),
        "airside_certified": True,
    },
    source_name="Примеры решений организатора → роботизация аэропорта → беспилотный тягач",
    source_url="https://cognitivepilot.com/",
    catalog_match=None,
    note=(
        "Круглогодичная работа на перроне, включая дождь, снег и туман. "
        "В каталоге организатора тягача нет, цена — оценочное допущение."
    ),
    restrictions=("Требуется допуск к работам в режимных зонах аэродрома",),
)

TRUCK_EVOCARGO = ReferenceSolution(
    slug="evocargo-n1",
    name="EVOCARGO N1",
    vendor="ООО «Эвокарго»",
    solution_type="autonomous_truck",
    object_types=("airport",),
    process_codes=("ground_handling", "waste", "terminal_logistics"),
    specs={
        "payload_kg": Decimal("2000"),
        **_m(5000, 1800, 2200),
        "autonomy_hours": Decimal("10"),
        "charge_time_min": Decimal("30"),
        "navigation_types": [
            "камеры", "лидары", "сенсоры", "автопилот 4–5 уровня автоматизации",
        ],
        "min_temp_c": Decimal("-40"),
        "max_temp_c": Decimal("50"),
        "lifetime_years": Decimal("10"),
        "battery_lifetime_years": Decimal("5"),
    },
    source_name="Примеры решений организатора → роботизация аэропорта → беспилотный грузовик",
    source_url="https://evocargo.com/",
    catalog_match="EVOCARGO N1",
    note=(
        "Аккумулятор 36 кВт·ч, запас хода 150–200 км, до 6 европаллет, "
        "работа 24/7 при −40…+50 °C."
    ),
    restrictions=("Требуется сертификация для работы в режимных зонах аэродрома",),
)

MEDICAL_AMR_RONAVI_SD = ReferenceSolution(
    slug="ronavi-sd",
    name="Ronavi SD",
    vendor="ООО «Ронави Роботикс»",
    solution_type="amr",
    object_types=("medical",),
    process_codes=("meals", "linen", "meds", "lab", "waste"),
    specs={
        "payload_kg": Decimal("10"),
        "own_weight_kg": Decimal("20"),
        **_m(420, 400, 200),
        "min_passage_width_m": Decimal("0.7"),
        "max_speed_mps": Decimal("2.5"),
        "autonomy_hours": Decimal("10"),
        "positioning_accuracy_mm": Decimal("3"),
        "navigation_types": ["QR-метки"],
        "min_temp_c": Decimal("5"),
        "max_temp_c": Decimal("40"),
        "lifetime_years": Decimal("7"),
        "battery_lifetime_years": Decimal("4"),
        "medical_sanitation_ready": True,
    },
    source_name="Примеры решений организатора → роботизация медучреждения → AMR",
    source_url="https://ronavi-robotics.ru/catalogue/sd",
    catalog_match="Ronavi SD",
    note="Сортировочный робот с откидной крышкой; проход 700 мм без запаса.",
)

MEDICAL_DELIVERY_PUDU = ReferenceSolution(
    slug="pudubot-2",
    name="PuduBot 2",
    vendor="Pudu Robotics",
    solution_type="delivery_robot",
    object_types=("medical",),
    process_codes=("meals", "linen", "meds", "supplies"),
    specs={
        "payload_kg": Decimal("10"),
        "own_weight_kg": Decimal("39"),
        **_m(580, 535, 1290),
        "min_passage_width_m": Decimal("0.8"),
        "max_speed_mps": Decimal("1.2"),
        "autonomy_hours": Decimal("12"),
        "charge_time_min": Decimal("240"),
        "navigation_types": ["VSLAM", "лазерный SLAM", "камера", "лидар", "3D-датчики глубины"],
        "min_temp_c": Decimal("0"),
        "max_temp_c": Decimal("40"),
        "lifetime_years": Decimal("7"),
        "battery_lifetime_years": Decimal("4"),
        "medical_sanitation_ready": True,
    },
    source_name="Примеры решений организатора → роботизация медучреждения → робот-доставщик",
    source_url="https://www.pudurobotics.com/en/products/pudubot2",
    catalog_match=None,
    note="Грузоподъёмность 10 кг на полку; скорость 0,5–1,2 м/с.",
    restrictions=("Требуется интеграция с дверями и лифтами",),
)

REFERENCE_SOLUTIONS: tuple[ReferenceSolution, ...] = (
    WAREHOUSE_AMR,
    WAREHOUSE_FMR,
    CLEANER_MARK2,
    SHUTTLE_STELCON,
    TUGGER_COGNITIVE,
    TRUCK_EVOCARGO,
    MEDICAL_AMR_RONAVI_SD,
    MEDICAL_DELIVERY_PUDU,
)

# Оценочные цены для решений, отсутствующих в каталоге организатора.
# Помечаются price_source = "estimate" и видны в интерфейсе как допущение.
PRICE_ESTIMATES: dict[str, Decimal] = {
    "stelcon-pallet-shuttle": Decimal("8500000"),
    "cognitive-pilot-tugger": Decimal("4200000"),
    "pudubot-2": Decimal("1200000"),
}
