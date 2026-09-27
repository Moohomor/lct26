"""Нормализация значений из файлов организатора.

Демо-файлы приходят в «человеческих» форматах: цены вида «2 700 000,00»,
числа с десятичной запятой, единицы измерения «м²» и булвы «Да»/«Нет».
Всё это приводится к типизированным значениям, которые уже можно хранить
в JSONB-параметрах проекта и считать по ним.
"""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Any

_NUM_CLEAN = re.compile(r"[^\d,.\-]")
_TRUE_TOKENS = {"да", "yes", "y", "true", "1", "имеется", "есть"}
_FALSE_TOKENS = {"нет", "no", "n", "false", "0", "отсутствует", "не имеется"}


def parse_number(value: Any) -> Decimal | None:
    """«2 700 000,00» → 2700000.00; «-25» → -25; пусто/текст → None."""
    if value is None:
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    raw = str(value).strip()
    if not raw or raw in {"-", "–", "—"}:
        return None
    cleaned = _NUM_CLEAN.sub("", raw.replace(" ", " ").replace(" ", ""))
    if not cleaned or cleaned in {"-", ".", ","}:
        return None
    # Запятая — десятичный разделитель; точка — разделитель тысяч.
    if "," in cleaned and "." in cleaned:
        cleaned = cleaned.replace(".", "").replace(",", ".")
    elif "," in cleaned:
        cleaned = cleaned.replace(",", ".")
    try:
        return Decimal(cleaned)
    except InvalidOperation:
        return None


def parse_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    token = str(value).strip().lower()
    if token in _TRUE_TOKENS:
        return True
    if token in _FALSE_TOKENS:
        return False
    return None


def parse_dimensions(value: Any) -> dict[str, float] | None:
    """«1200×800×1600» или «1200x800x1600» → {"length": .., "width": .., "height": ..}."""
    if value is None:
        return None
    parts = re.split(r"[×xхX]", str(value).strip())
    if len(parts) != 3:
        return None
    dims: dict[str, float] = {}
    for key, part in zip(("length", "width", "height"), parts, strict=True):
        num = parse_number(part)
        if num is None:
            return None
        dims[key] = float(num)
    return dims


def clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFKC", str(value)).strip()
    text = re.sub(r"\s+", " ", text)
    return text or None


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for v in values:
        key = v.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(v.strip())
    return out
