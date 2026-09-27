"""Командная строка обслуживания базы данных.

    python -m app.scripts.db reset      # удалить все таблицы и создать заново
    python -m app.scripts.db seed       # загрузить данные организатора
    python -m app.scripts.db seed -f    # перезагрузить, обновив существующие записи
    python -m app.scripts.db status     # что сейчас лежит в базе
    python -m app.scripts.db demo       # демонстрационные проекты и сценарии

Команды идемпотентны: `seed` можно запускать при каждом старте приложения,
`reset` требует явного подтверждения.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Поддержка запуска файла напрямую: python app/scripts/db.py
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from sqlalchemy import text  # noqa: E402

from app.core.db import Base, SessionLocal, engine  # noqa: E402


def cmd_reset(args: argparse.Namespace) -> int:
    if not args.force:
        print("Удаление всех данных требует --force.", file=sys.stderr)
        return 2
    # DROP ... CASCADE вместо Base.metadata.drop_all: внешние ключи между
    # таблицами требуют правильного порядка, а drop_all такой порядок не
    # гарантирует на стороне СУБД.
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
    Base.metadata.create_all(engine)
    print("Схема пересоздана.")
    return 0


def cmd_seed(args: argparse.Namespace) -> int:
    from app.seed.seed import run_seed

    with SessionLocal() as db:
        report = run_seed(db, force=args.force)
        print(json.dumps(report.as_dict(), ensure_ascii=False, indent=2))
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    from app.seed.seed import seed_summary

    with SessionLocal() as db:
        print(json.dumps(seed_summary(db), ensure_ascii=False, indent=2))
    return 0


def cmd_demo(args: argparse.Namespace) -> int:
    from app.seed.demo import build_demo_projects

    with SessionLocal() as db:
        report = build_demo_projects(db, force=args.force)
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    reset = sub.add_parser("reset", help="пересоздать схему")
    reset.add_argument("-f", "--force", action="store_true")
    reset.set_defaults(func=cmd_reset)

    seed = sub.add_parser("seed", help="загрузить данные организатора")
    seed.add_argument(
        "-f", "--force", action="store_true", help="обновить существующие записи"
    )
    seed.set_defaults(func=cmd_seed)

    status = sub.add_parser("status", help="сводка по данным в базе")
    status.set_defaults(func=cmd_status)

    demo = sub.add_parser("demo", help="демонстрационные проекты и расчёты")
    demo.add_argument("-f", "--force", action="store_true")
    demo.set_defaults(func=cmd_demo)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
