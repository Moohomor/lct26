"""Перегенерирует requirements.txt с хешами под целевую версию Python.

Зачем: список был выгружен `uv export` для Python 3.14 (см. .python-version),
а образ собирается на 3.12. Хешей для cp312-колёс в файле нет, поэтому в
--require-hashes режиме pip не может взять готовое колесо и каждый раз
собирает пакет из sdist — на Render это десятки минут на сборку.

Скрипт берёт зафиксированные версии из requirements.txt и подставляет
хеши всех файлов релиза, чтобы колесо нашлось под любую платформу.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.request

SOURCE = "requirements.txt"
OUT = "requirements.txt"
HEADER = """\
# Зависимости проекта.
#
# Файл собран скриптом scripts/regenerate_requirements.py: версии
# зафиксированы по .venv, а хеши взяты со всех файлов релиза на PyPI.
#
# Хеши обязательны: если у пакета есть хотя бы один, pip включает режим
# --require-hashes и требует хеш у КАЖДОГО пакета, включая транзитивные.
# Прямое `pip install alembic` без строки с хешами здесь не сработает.
#
# ВАЖНО: хеши перечислены для всех файлов релиза (sdist и колёса всех
# платформ), а не только для текущей. Так список остаётся рабочим и на
# Render (linux/amd64), и на macOS, и после смены версии Python в образе.
# Если после правки версий файл поехал — перегенерируйте:
#
#     python scripts/regenerate_requirements.py
"""


def pinned() -> list[str]:
    """Достаёт «имя==версия» из текущего requirements.txt, сохраняя порядок."""
    text = open(SOURCE, encoding="utf-8").read()
    specs: list[str] = []
    for match in re.finditer(r"^([A-Za-z0-9._-]+)==([^\s\\]+)", text, re.M):
        spec = f"{match.group(1)}=={match.group(2)}"
        if spec not in specs:
            specs.append(spec)
    return specs


def hashes_for(spec: str) -> list[str]:
    name, version = spec.split("==", 1)
    url = f"https://pypi.org/pypi/{name}/json"
    with urllib.request.urlopen(url, timeout=90) as response:
        data = json.load(response)
    # В JSON PyPI releases[version] — список файлов релиза, а не словарь.
    files = data["releases"].get(version, [])
    if not files:
        raise SystemExit(
            f"{spec}: на PyPI нет файлов для этой версии. "
            "Версия, возможно, указана вручную и не существует."
        )
    found: list[str] = []
    for meta in files:
        digest = meta["digests"]["sha256"]
        if digest not in found:
            found.append(digest)
    return found


def main() -> int:
    specs = pinned()
    print(f"Пакетов в {SOURCE}: {len(specs)}")
    blocks: list[str] = []
    for index, spec in enumerate(specs, 1):
        name, _ = spec.split("==", 1)
        try:
            digests = hashes_for(spec)
        except SystemExit as exc:
            print(f"  {exc}")
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"  {name}: сеть недоступна ({exc})")
            return 2
        lines = [f"{spec} \\"]
        for i, digest in enumerate(digests):
            tail = " \\" if i < len(digests) - 1 else ""
            lines.append(f"    --hash=sha256:{digest}{tail}")
        blocks.append("\n".join(lines))
        print(f"  [{index:>3}/{len(specs)}] {spec:<28} {len(digests):>3} файлов")

    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write(HEADER)
        handle.write("\n".join(blocks) + "\n")
    print(f"\nЗаписан {OUT}: {len(blocks)} пакетов.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
