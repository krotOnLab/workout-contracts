"""Проверка каталогов, профилей и конформанс-векторов."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from workout_contracts_tools.catalogs import load_catalogs, repo_root

ROOT = repo_root(Path(__file__))
CATALOGS = load_catalogs(ROOT)
CASES = sorted((ROOT / "conformance" / "cases").glob("*.json"))


def test_catalogs_consistent() -> None:
    load_catalogs(ROOT)


def test_every_mvp_command_has_profile_support() -> None:
    desktop = next(p for p in CATALOGS["profiles"]["profiles"] if p["name"] == "desktop-mvp")
    mvp_commands = {c["wire"] for c in CATALOGS["commands"]["commands"] if c["mvp"]}
    assert mvp_commands <= set(desktop["supported_commands"])


def test_reserved_commands_unsupported_in_mvp() -> None:
    desktop = next(p for p in CATALOGS["profiles"]["profiles"] if p["name"] == "desktop-mvp")
    assert "pause" not in desktop["supported_commands"]
    assert "resume" not in desktop["supported_commands"]


@pytest.mark.parametrize("path", CASES, ids=lambda p: p.name)
def test_case_schema_and_event_names(path: Path) -> None:
    schema = json.loads(
        (ROOT / "schema" / "conformance-case.schema.json").read_text(encoding="utf-8")
    )
    case = json.loads(path.read_text(encoding="utf-8"))
    Draft202012Validator(schema).validate(case)

    known = {e["wire"] for e in CATALOGS["events"]["events"]}
    for expected in case["expect"]["events"]:
        assert expected["name"] in known, f"{path.name}: неизвестное событие {expected['name']}"


def test_case_ids_unique() -> None:
    ids = [json.loads(p.read_text(encoding="utf-8"))["case_id"] for p in CASES]
    assert len(ids) == len(set(ids))