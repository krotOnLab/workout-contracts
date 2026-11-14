# SPDX-License-Identifier: Apache-2.0
"""Исключения инструментария контрактов."""

from __future__ import annotations


class ContractError(Exception):
    """Нарушение контракта с машинным кодом ошибки.

    Attributes
    ----------
    code : str
        Код из `catalogs/errors.json`, например `CFG_003`.
    detail : str
        Человекочитаемое пояснение, пригодное для вывода в CLI.
    """

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


class CatalogError(ContractError):
    """Несогласованность каталогов между собой."""