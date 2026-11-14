# SPDX-License-Identifier: Apache-2.0
"""Нормализация документа тренировки в каноническое представление."""

from __future__ import annotations

import json
from typing import Any


def to_canonical(data: dict[str, Any]) -> dict[str, Any]:
    """Привести документ к каноническому виду для обмена между платформами.

    Parameters
    ----------
    data : dict[str, Any]
        Валидный документ тренировки.

    Returns
    -------
    dict[str, Any]
        Канонический документ: целые `duration_ms`, явные `stage_id`,
        проставленные значения по умолчанию, без блока `runtime`.

    Notes
    -----
    Функция идемпотентна и принимает как пользовательский, так и уже
    канонический документ. Валидация должна выполняться до вызова.
    """
    workout = data["workout"]
    stages: list[dict[str, Any]] = []

    for index, stage in enumerate(workout["stages"], start=1):
        canonical: dict[str, Any] = {
            "stage_id": stage.get("stage_id", f"st-{index:02d}"),
            "type": stage["type"],
            "name": stage["name"],
            "completion": stage["completion"],
        }
        if stage["completion"] == "timed":
            canonical["duration_ms"] = _to_ms(stage)
        for optional in ("description", "announcement_key", "allow_skip"):
            if stage.get(optional) is not None:
                canonical[optional] = stage[optional]
        stages.append(canonical)

    canonical_workout: dict[str, Any] = {
        "workout_id": workout["workout_id"],
        "name": workout["name"],
        "countdown_seconds": workout.get("countdown_seconds", 5),
        "stages": stages,
    }
    if workout.get("description") is not None:
        canonical_workout["description"] = workout["description"]

    return {"schema_version": data["schema_version"], "workout": canonical_workout}


def dumps_canonical(document: dict[str, Any]) -> str:
    """Сериализовать канонический документ детерминированно.

    Returns
    -------
    str
        JSON с отсортированными ключами, UTF-8 символами без экранирования,
        отступом 2 и завершающим переводом строки.
    """
    return json.dumps(document, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _to_ms(stage: dict[str, Any]) -> int:
    """Получить длительность в целых миллисекундах.

    Notes
    -----
    Округление half-up: `floor(x * 1000 + 0.5)`. Правило зафиксировано
    в ADR-0002 и должно совпадать во всех реализациях.
    """
    if "duration_ms" in stage:
        return int(stage["duration_ms"])
    return int(float(stage["duration_sec"]) * 1000 + 0.5)