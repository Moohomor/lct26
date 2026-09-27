"""Экспорт результатов: PDF-отчёт по расчёту.

Отчёт строится из сохранённого снимка, поэтому доступ к нему проверяется так
же, как доступ к самому расчёту: владелец проекта или администратор.
"""

from fastapi import APIRouter, Query, status
from fastapi.responses import Response

from app.core.deps import DbSession, LoggedIn, ensure_owner_or_admin
from app.models import Calculation, Project, Scenario

router = APIRouter(tags=["export"])


def _load_calculation(db: DbSession, user, calculation_id: int) -> Calculation:
    """Расчёт с проверкой прав: чужой расчёт не отдаётся даже администратору молча."""
    calc = db.get(Calculation, calculation_id)
    if calc is None:
        from app.core.errors import AppError

        raise AppError("Расчёт не найден.", code="not_found", status_code=404)
    scenario = db.get(Scenario, calc.scenario_id)
    project = db.get(Project, scenario.project_id) if scenario else None
    if project is None:
        from app.core.errors import AppError

        raise AppError("Проект расчёта не найден.", code="not_found", status_code=404)
    ensure_owner_or_admin(user, project.user_id)
    return calc


_TRANSLIT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "yo",
    "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
    "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
    "ф": "f", "х": "h", "ц": "ts", "ч": "ch", "ш": "sh", "щ": "sch",
    "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
}


def _latin(name: str) -> str:
    """Транслитерация кириллицы: имя файла обязано быть ASCII.

    `str.isalnum()` считает кириллические буквы буквами, поэтому фильтр
    «только буквы и цифры» их пропускает — и кириллица попадает в заголовок
    Content-Disposition, который кодируется в latin-1 и падает с
    UnicodeEncodeError. Транслитерация решает это без потери читаемости.
    """
    out: list[str] = []
    for char in name.lower():
        if char in _TRANSLIT:
            out.append(_TRANSLIT[char])
        elif char.isascii() and char.isalnum():
            out.append(char)
        elif char in "-_":
            out.append(char)
        else:
            out.append("_")
    slug = "".join(out)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "raschet"


def _pdf_response(calc: Calculation, content: bytes) -> Response:
    """Отдаёт PDF с именем файла, по которому видно, что внутри."""
    from datetime import datetime
    from urllib.parse import quote

    project = calc.scenario.project if calc.scenario else None
    name = (project.name if project else "raschet").strip() or "raschet"
    stamp = (calc.computed_at or datetime.now()).strftime("%Y%m%d")
    # filename — ASCII-транслит для старых клиентов, filename* — исходное
    # имя в UTF-8 по RFC 5987. Браузер выбирает то, что понимает.
    filename = f"{_latin(name)}-{stamp}.pdf"
    disposition = (
        f"attachment; filename=\"{filename}\"; "
        f"filename*=UTF-8''{quote(name)}-{stamp}.pdf"
    )
    return Response(
        content=content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": disposition,
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get(
    "/calculations/{calculation_id}/export/pdf",
    responses={200: {"content": {"application/pdf": {}}}},
    status_code=status.HTTP_200_OK,
)
def export_calculation_pdf(
    calculation_id: int,
    db: DbSession,
    user: LoggedIn,
    inline: bool = Query(default=False, description="Показать в браузере, а не скачать"),
) -> Response:
    """PDF-отчёт по расчёту: состав оборудования, сценарии, TCO, допущения."""
    from app.services.reports.pdf import build_report

    calc = _load_calculation(db, user, calculation_id)
    content = build_report(calc)
    response = _pdf_response(calc, content)
    if inline:
        response.headers["Content-Disposition"] = "inline"
    return response
