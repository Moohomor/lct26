"""Привязывает фотографии решений к позициям каталога.

Снимки выгружены из «Каталога внедрения» ФЦ БАС и лежат в
app/assets/solutions, а связи «название позиции → файл» — в
app/assets/solution_photos.json. Импорт идемпотентен: при повторном
запуске путь перезаписывается тем же значением, лишние файлы не плодятся.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Solution

MANIFEST_NAME = "solution_photos.json"


@dataclass
class PhotoImportResult:
    assigned: int = 0
    files_missing: list[str] = None  # type: ignore[assignment]
    names_missing: list[str] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.files_missing is None:
            self.files_missing = []
        if self.names_missing is None:
            self.names_missing = []

    def as_dict(self) -> dict[str, object]:
        return {
            "assigned": self.assigned,
            "files_missing": self.files_missing,
            "names_missing": self.names_missing,
        }


def _norm(name: str) -> str:
    return " ".join(name.lower().replace("ё", "е").split())


def import_solution_photos(db: Session) -> PhotoImportResult:
    result = PhotoImportResult()
    manifest_path: Path = settings.assets_dir / MANIFEST_NAME
    if not manifest_path.exists():
        result.names_missing.append(f"нет манифеста {manifest_path.name}")
        return result

    manifest: dict[str, str] = json.loads(manifest_path.read_text(encoding="utf-8"))
    by_name = {_norm(s.name): s for s in db.scalars(select(Solution))}

    for name, rel in manifest.items():
        if not (settings.assets_dir / rel).exists():
            result.files_missing.append(rel)
            continue
        solution = by_name.get(_norm(name))
        if solution is None:
            result.names_missing.append(name)
            continue
        solution.photo_file = rel
        result.assigned += 1

    db.flush()
    return result
