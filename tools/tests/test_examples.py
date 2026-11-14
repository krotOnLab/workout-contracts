"""Проверка примеров и свойств нормализации."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from workout_contracts_tools.catalogs import load_catalogs, repo_root
from workout_contracts_tools.errors import ContractError
from workout_contracts_tools.normalization import dumps_canonical, to_canonical
from workout_contracts_tools.validation import load_document, validate_document

ROOT = repo_root(Path(__file__))
CATALOGS = load_catalogs(ROOT)
KEYS = {n["key"] for n in CATALOGS["notifications"]["notifications"]}
VALID = sorted((ROOT / "examples" / "valid").glob("*.yaml"))
INVALID = sorted((ROOT / "examples" / "invalid").glob("*.yaml"))


@pytest.mark.parametrize("path", VALID, ids=lambda p: p.name)
def test_valid_examples(path: Path) -> None:
    document = load_document(path)
    validate_document(document, ROOT / "schema", notification_keys=KEYS)


@pytest.mark.parametrize("path", INVALID, ids=lambda p: p.name)
def test_invalid_examples(path: Path) -> None:
    with pytest.raises(ContractError):
        document = load_document(path)
        validate_document(document, ROOT / "schema", notification_keys=KEYS)


def test_normalization_is_idempotent() -> None:
    document = load_document(ROOT / "examples" / "valid" / "home-workout-001.yaml")
    once = to_canonical(document)
    assert to_canonical(once) == once


def test_canonical_fixture_matches() -> None:
    document = load_document(ROOT / "examples" / "valid" / "home-workout-001.yaml")
    expected = json.loads(
        (ROOT / "examples" / "valid" / "home-workout-001.canonical.json").read_text(encoding="utf-8")
    )
    assert to_canonical(document) == expected


def test_runtime_is_dropped() -> None:
    document = load_document(ROOT / "examples" / "valid" / "home-workout-001.yaml")
    assert "runtime" not in to_canonical(document)


def test_deterministic_serialization() -> None:
    document = load_document(ROOT / "examples" / "valid" / "timed-only.yaml")
    canonical = to_canonical(document)
    assert dumps_canonical(canonical) == dumps_canonical(to_canonical(canonical))