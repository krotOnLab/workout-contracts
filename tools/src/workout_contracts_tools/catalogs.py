# SPDX-License-Identifier: Apache-2.0
"""Загрузка и кросс-проверка каталогов контрактов."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import CatalogError

CATALOG_NAMES = ("states", "commands", "events", "errors", "notifications", "profiles")


def repo_root(start: Path | None = None) -> Path:
    """Найти корень репозитория контрактов по наличию каталога `catalogs`.

    Parameters
    ----------
    start : Path | None
        Каталог начала поиска. По умолчанию — текущий рабочий каталог.

    Returns
    -------
    Path
        Каталог, содержащий `catalogs` и `schema`.

    Raises
    ------
    CatalogError
        Корень не найден ни в `start`, ни в его родителях.
    """
    current = (start or Path.cwd()).resolve()
    for candidate in (current, *current.parents):
        if (candidate / "catalogs").is_dir() and (candidate / "schema").is_dir():
            return candidate
    raise CatalogError("CFG_001", "корень репозитория контрактов не найден")


def load_catalogs(root: Path) -> dict[str, Any]:
    """Прочитать все каталоги и проверить их согласованность.

    Parameters
    ----------
    root : Path
        Корень репозитория контрактов.

    Returns
    -------
    dict[str, Any]
        Отображение имени каталога в его содержимое.

    Raises
    ------
    CatalogError
        Католог отсутствует, содержит дубликаты или ссылается
        на несуществующие сущности.
    """
    data: dict[str, Any] = {}
    for name in CATALOG_NAMES:
        path = root / "catalogs" / f"{name}.json"
        if not path.is_file():
            raise CatalogError("CFG_001", f"каталог не найден: {path}")
        data[name] = json.loads(path.read_text(encoding="utf-8"))

    _check_consistency(data)
    return data


def _check_consistency(data: dict[str, Any]) -> None:
    """Проверить ссылки между каталогами.

    Notes
    -----
    Проверяются уникальность имён и кодов, существование состояний
    и событий, на которые ссылаются команды, уведомления и профили.
    """
    states = _unique([s["wire"] for s in data["states"]["states"]], "states")
    commands = _unique([c["wire"] for c in data["commands"]["commands"]], "commands")
    events = _unique([e["wire"] for e in data["events"]["events"]], "events")
    _unique([e["code"] for e in data["errors"]["errors"]], "errors")
    _unique([n["key"] for n in data["notifications"]["notifications"]], "notifications")

    known_events = set(events)
    for command in data["commands"]["commands"]:
        for state in command["allowed_states"]:
            if state not in states:
                raise CatalogError("CFG_003", f"{command['wire']}: неизвестное состояние {state}")
        target = command.get("success_event")
        if target is not None and target not in known_events:
            raise CatalogError("CFG_003", f"{command['wire']}: неизвестное событие {target}")

    for note in data["notifications"]["notifications"]:
        if note["event"] not in known_events:
            raise CatalogError("CFG_003", f"{note['key']}: неизвестное событие {note['event']}")

    for profile in data["profiles"]["profiles"]:
        for wire in profile["supported_commands"]:
            if wire not in commands:
                raise CatalogError("CFG_003", f"{profile['name']}: неизвестная команда {wire}")


def _unique(values: list[str], catalog: str) -> list[str]:
    """Убедиться в отсутствии дубликатов."""
    duplicates = {v for v in values if values.count(v) > 1}
    if duplicates:
        raise CatalogError("CFG_008", f"{catalog}: дубликаты {sorted(duplicates)}")
    return values