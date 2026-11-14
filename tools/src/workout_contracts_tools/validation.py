# SPDX-License-Identifier: Apache-2.0
"""Валидация документов тренировки: схема и семантика."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .errors import ContractError

SUPPORTED_SCHEMA_VERSION = 1


def load_document(path: Path) -> dict[str, Any]:
    """Прочитать YAML или JSON документ тренировки.

    Parameters
    ----------
    path : Path
        Путь к файлу `.yaml`, `.yml` или `.json`.

    Returns
    -------
    dict[str, Any]
        Разобранный документ.

    Raises
    ------
    ContractError
        Файл не найден (`CFG_001`), не читается или не разбирается (`CFG_002`),
        либо корень документа не является объектом (`CFG_003`).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ContractError("CFG_001", f"файл не найден: {path}") from exc
    except OSError as exc:
        raise ContractError("CFG_002", f"файл не читается: {path}: {exc}") from exc

    try:
        data = yaml.safe_load(text) if path.suffix in {".yaml", ".yml"} else json.loads(text)
    except (yaml.YAMLError, json.JSONDecodeError) as exc:
        raise ContractError("CFG_002", f"ошибка разбора {path}: {exc}") from exc

    if not isinstance(data, dict):
        raise ContractError("CFG_003", "корень документа должен быть объектом")
    return data


def validate_document(
    data: dict[str, Any],
    schema_dir: Path,
    *,
    profile: dict[str, Any] | None = None,
    notification_keys: set[str] | None = None,
) -> list[str]:
    """Проверить документ по схеме и семантическим правилам.

    Parameters
    ----------
    data : dict[str, Any]
        Разобранный документ тренировки.
    schema_dir : Path
        Каталог со схемами JSON Schema.
    profile : dict[str, Any] | None
        Профиль возможностей. Задаёт лимиты этапов и длительностей.
    notification_keys : set[str] | None
        Известные ключи озвучки. Неизвестный ключ даёт предупреждение `CFG_011`.

    Returns
    -------
    list[str]
        Предупреждения в формате `CODE: сообщение`. Пустой список означает
        отсутствие замечаний.

    Raises
    ------
    ContractError
        Нарушение схемы (`CFG_003`), неподдерживаемая версия (`CFG_009`),
        дубликаты `stage_id` (`CFG_008`), недопустимая длительность (`CFG_005`)
        или превышение лимитов профиля (`CFG_010`).

    Notes
    -----
    Схема не проверяет уникальность `stage_id` и точность длительности:
    это семантические правила, вынесенные сюда намеренно.
    """
    version = data.get("schema_version")
    if version != SUPPORTED_SCHEMA_VERSION:
        raise ContractError("CFG_009", f"поддерживается только schema_version=1, получено {version!r}")

    schema = json.loads((schema_dir / "workout.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path))
    if errors:
        first = errors[0]
        location = "/".join(str(p) for p in first.absolute_path) or "<root>"
        raise ContractError("CFG_003", f"{location}: {first.message}")

    workout = data["workout"]
    stages = workout["stages"]
    warnings: list[str] = []

    limits = (profile or {}).get("limits", {})
    max_stages = limits.get("max_stages", 512)
    min_ms = limits.get("min_duration_ms", 100)
    max_ms = limits.get("max_duration_ms", 86_400_000)
    max_countdown = limits.get("max_countdown_seconds", 10)
    countdown = workout.get("countdown_seconds", 5)

    if len(stages) > max_stages:
        raise ContractError("CFG_010", f"этапов {len(stages)}, лимит профиля {max_stages}")

    if countdown > max_countdown:
        raise ContractError(
            "CFG_010",
            f"countdown_seconds={countdown} превышает лимит профиля {max_countdown}",
        )

    seen: set[str] = set()
    for index, stage in enumerate(stages, start=1):
        stage_id = stage.get("stage_id", f"st-{index:02d}")
        if stage_id in seen:
            raise ContractError("CFG_008", f"дублирующийся stage_id: {stage_id}")
        seen.add(stage_id)

        if stage["completion"] == "timed":
            duration_ms = int(stage["duration_sec"] * 1000 + 0.5)
            if not min_ms <= duration_ms <= max_ms:
                raise ContractError(
                    "CFG_005",
                    f"{stage_id}: длительность {duration_ms} мс вне диапазона {min_ms}..{max_ms}",
                )

        key = stage.get("announcement_key")
        if key and notification_keys is not None and key not in notification_keys:
            warnings.append(f"CFG_011: {stage_id}: неизвестный announcement_key {key}")

    if _has_suspicious_sequence(stages):
        warnings.append("CFG_012: подряд идут несколько этапов отдыха")

    return warnings


def _has_suspicious_sequence(stages: list[dict[str, Any]]) -> bool:
    """Обнаружить два и более этапа отдыха подряд."""
    previous_rest = False
    for stage in stages:
        current_rest = stage["type"] == "rest"
        if current_rest and previous_rest:
            return True
        previous_rest = current_rest
    return False