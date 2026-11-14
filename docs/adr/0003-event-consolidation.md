# ADR-0003. Консолидация событий этапов

## Статус
Принято

## Контекст
В архитектурном документе v0.1 присутствовали пары `StageStarted` +
`ExerciseStarted` / `RestStarted` и тройка `TimerExpired` / `StageCompleted` /
`StageSkipped`. Дублирование создаёт вопрос о порядке публикации и риск
расхождения реализаций.

## Решение
- `stage.started` c `payload.stage_type` вместо отдельных событий типа этапа.
- `stage.finished` c `payload.reason` ∈ {timer_expired, confirmed, skipped}
  вместо трёх событий завершения.

Различение сигналов и фраз переносится в каталог уведомлений через `match`.

## Соответствие имён v0.1

| v0.1 | Контракт v1 |
|---|---|
| StageStarted + ExerciseStarted | stage.started{stage_type: exercise} |
| StageStarted + RestStarted | stage.started{stage_type: rest} |
| TimerExpired | stage.finished{reason: timer_expired} |
| StageCompleted | stage.finished{reason: confirmed} |
| StageSkipped | stage.finished{reason: skipped} |
| WaitingConfirmation | stage.waiting_confirmation |
| CountdownTick | stage.countdown |

## Следствия
Меньше событий, один инвариант «одно завершение на этап», проще тесты и
прошивка. Стоимость: адаптеру нужен `match` по payload, а не только по имени.

## Подтверждение

Решение подтверждено заказчиком. Все конформанс-векторы контрактов v1
используют консолидированные события:

- `stage.started` с `payload.stage_type`;
- `stage.finished` с `payload.reason`.

Отдельные события `exercise.started`, `rest.started`, `timer.expired`,
`stage.completed`, `stage.skipped` в протокол v1 не вводятся.