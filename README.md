# workout-contracts

Контракты тренировочного приложения: формат конфигурации, команды, события,
состояния, ошибки, каталог уведомлений и конформанс-векторы.

Репозиторий **не содержит** движка тренировки, UI, звука и голосовых адаптеров.
Он содержит только то, что обязаны одинаково понимать все реализации.

## Потребители

| Платформа | Стек | Профиль |
|---|---|---|
| Desktop / Linux | Python 3.11+ | `desktop-mvp` |
| Android | Kotlin | `android-v1` |
| ESP32 | C/C++ (ESP-IDF) | `esp32-v1` |

## Слои контрактов

1. `schema/` — машинная валидация документов (JSON Schema 2020-12).
2. `catalogs/` — машинные справочники состояний, команд, событий, ошибок,
   уведомлений и профилей возможностей.
3. `docs/` — нормативная семантика: переходы, тайминги, порядок событий.
4. `conformance/` — исполняемые векторы поведения, общие для всех платформ.

Правило: если поведение нельзя проверить конформанс-вектором или схемой,
оно не считается частью контракта.

## Быстрый старт

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e "tools[dev]"

wc-contracts check-catalogs
wc-contracts validate examples/valid/home-workout-001.yaml
wc-contracts export examples/valid/home-workout-001.yaml -o /tmp/workout.json
pytest tools/tests
```

## Ключевые инварианты

- Ядро не зависит от платформы, консоли, звука и микрофона.
- `CONFIRM` подтверждает выполнение ручного этапа, `NEXT` пропускает этап.
  Это разные команды с разными событиями результата.
- Все временные величины в каноническом представлении — целые миллисекунды.
- Время монотонное, отсчёт от начала сессии; настенные часы не используются.
- События образуют строгую последовательность с непрерывным `seq`.

## Версионирование

`VERSION` — версия пакета контрактов (SemVer).
`schema_version` — версия формата конфигурации (целое).
См. `docs/versioning.md`.

## Архитектура и стратегия репозиториев

Общая архитектура проекта и глобальные ADR хранятся в репозитории `workout-docs`.

- Архитектурный документ: `workout-docs/architecture/architecture.md`
- Стратегия мультирепозиторной архитектуры: `workout-docs/adr/0001-multi-repo-strategy.md`

Нормативная часть протокола находится в текущем репозитории:
`schema/`, `catalogs/`, `conformance/`, `docs/protocol.md`.

## Идентификаторы схем

JSON Schema используют канонические `$id`, привязанные к репозиторию:

```text
https://github.com/krotOnLab/workout-contracts/schema/...
```

## Подключение платформами

Платформы подключают контракты через Git Submodule.

Пример для платформенного репозитория:

```bash
git submodule add https://github.com/krotOnLab/workout-contracts contracts
git submodule update --init --recursive
```

Фиксация версии контрактов:

```bash
git -C contracts checkout v0.1.0
git add contracts
git commit -m "chore: pin workout-contracts v0.1.0"
```

Платформы потребляют:

- `schema/`
- `catalogs/`
- `conformance/`
- `examples/`
- нормативные документы из `docs/`

Платформы не обязаны использовать `tools/` как библиотеку. `tools/` является
референсным инструментарием для проверки контрактов.

## Нормативность документов

Нормативными являются:

- `schema/`
- `catalogs/`
- `conformance/`
- `docs/protocol.md`
- `docs/timing.md`
- `docs/versioning.md`
- `docs/conformance.md`
- принятые ADR из `docs/adr/`

Документы в `workout-docs` являются контекстной архитектурной документацией.
При расхождении между `workout-docs` и `workout-contracts` приоритет имеют
контракты из `workout-contracts`.

## Лицензия

Репозиторий распространяется под лицензией Apache-2.0.

Полный текст лицензии находится в файле `LICENSE`.

Референсный Python-инструментарий в каталоге `tools/` также распространяется
под Apache-2.0.

