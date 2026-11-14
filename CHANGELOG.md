# Changelog

## 0.1.0 — 2026-11-13

### Added
- JSON Schema: workout, session-state, view-state, conformance-case.
- Каталоги: states, commands, events, errors, notifications, profiles.
- Нормативные документы: protocol, timing, versioning, conformance.
- ADR-0001..0005.
- Конформанс-векторы cf-001..cf-010.
- Примеры валидных и невалидных конфигов.
- Референсный инструментарий: validate, export, check-catalogs.
- Тесты инструментария и CI.
- Лицензия Apache-2.0.
- Канонические `$id` схем, привязанные к репозиторию.
- Подтверждённые лимиты профилей:
  - desktop/android: `min_duration_ms=100`, `max_stages=512`;
  - esp32: `min_duration_ms=1000`, `max_stages=128`;
  - все профили: `countdown_seconds=0..10`.

### Changed
- Консолидация событий этапов относительно архитектурного документа v0.1:
  `stage.started{stage_type}`, `stage.finished{reason}`.
- `runtime` остаётся необязательным блоком в пользовательском документе
  тренировки и удаляется при нормализации в канонический JSON.
- Автогенерация `stage_id` в форме `st-NN` принята как допустимая для ручных
  конфигов; будущий редактор тренировок обязан использовать стабильные ID.

### Closed
- Q-CONTRACTS-001: консолидация событий подтверждена.
- Q-CONTRACTS-002: позиционная автогенерация `stage_id` принята.
- Q-CONTRACTS-003: `runtime` остаётся в том же файле.
- Лимиты профилей подтверждены.
- Формальные реквизиты: Apache-2.0, канонические `$id`, submodule для всех платформ.

### Open
- Подставить реальный `<org>` в `$id` и `[project.urls]` перед релизным тегом.
- Указать реального правообладателя в `LICENSE`, если требуется.