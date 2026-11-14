# SPDX-License-Identifier: Apache-2.0
"""CLI инструментария контрактов."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .catalogs import load_catalogs, repo_root
from .errors import ContractError
from .normalization import dumps_canonical, to_canonical
from .validation import load_document, validate_document


def build_parser() -> argparse.ArgumentParser:
    """Собрать парсер аргументов CLI."""
    parser = argparse.ArgumentParser(prog="wc-contracts", description="Инструменты контрактов")
    parser.add_argument("--root", type=Path, default=None, help="корень репозитория контрактов")
    sub = parser.add_subparsers(dest="command", required=True)

    validate = sub.add_parser("validate", help="проверить документ тренировки")
    validate.add_argument("path", type=Path)
    validate.add_argument("--profile", default=None, help="имя профиля из catalogs/profiles.json")

    export = sub.add_parser("export", help="экспортировать канонический JSON")
    export.add_argument("path", type=Path)
    export.add_argument("-o", "--output", type=Path, default=None)
    export.add_argument("--profile", default=None)

    sub.add_parser("check-catalogs", help="проверить согласованность каталогов")
    return parser


def main(argv: list[str] | None = None) -> int:
    """Точка входа CLI.

    Returns
    -------
    int
        Код возврата: 0 — успех, 2 — ошибка контракта, 1 — внутренняя ошибка.
    """
    args = build_parser().parse_args(argv)
    try:
        root = args.root or repo_root()
        catalogs = load_catalogs(root)

        if args.command == "check-catalogs":
            print("каталоги согласованы")
            return 0

        profile = _select_profile(catalogs, getattr(args, "profile", None))
        keys = {n["key"] for n in catalogs["notifications"]["notifications"]}
        document = load_document(args.path)
        warnings = validate_document(
            document, root / "schema", profile=profile, notification_keys=keys
        )
        for warning in warnings:
            print(f"warning: {warning}", file=sys.stderr)

        if args.command == "validate":
            print(f"OK: {args.path}")
            return 0

        canonical = dumps_canonical(to_canonical(document))
        if args.output:
            args.output.write_text(canonical, encoding="utf-8")
            print(f"записано: {args.output}")
        else:
            sys.stdout.write(canonical)
        return 0

    except ContractError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


def _select_profile(catalogs: dict, name: str | None) -> dict | None:
    """Найти профиль по имени."""
    if name is None:
        return None
    for profile in catalogs["profiles"]["profiles"]:
        if profile["name"] == name:
            return profile
    raise ContractError("CFG_003", f"неизвестный профиль: {name}")


if __name__ == "__main__":
    raise SystemExit(main())