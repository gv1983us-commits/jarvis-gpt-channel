# Единый операционный GitHub workflow

Машиночитаемая версия: [`GITHUB_OPERATIONAL_WORKFLOW.json`](GITHUB_OPERATIONAL_WORKFLOW.json).

Этот workflow собирает в один исполнимый порядок:

```text
задача
→ проверка текущей формы и среды
→ выбор репозитория
→ проверка полномочий
→ закрепление source revision
→ ветка
→ изменение
→ tests / CI
→ BEC receipt
→ draft PR
→ review
→ merge authority
→ merge по expected head SHA
→ post-merge verification
→ CDTS / PCA handoff
→ закрытие
```

Он не выдаёт полномочия, не заменяет владельца репозитория и не превращает технический доступ в разрешение на любое действие.

## 1. Intake

Зафиксировать:

- `task_id`;
- исходный запрос;
- ожидаемый результат;
- критерии приёмки;
- явно названные запреты и границы.

Не начинать с выбора инструмента. Сначала определяется объект изменения и требуемый результат.

## 2. Capability probe

До записи проверить именно текущую форму в текущей среде:

```text
tool present
→ permission known
→ call possible
→ observable result
→ addressable evidence
```

Для лимитов используются четыре состояния:

- `exposed` — значение показано средой;
- `documented` — значение подтверждено документацией;
- `observed_lower_bound` — фактически пройдено не меньше указанного;
- `unknown` — максимум не раскрыт и не был достигнут.

`observed_lower_bound` нельзя выдавать за максимум.

Актуальный снимок среды хранится в [`reports/2026-08-04-current-environment-capabilities.json`](reports/2026-08-04-current-environment-capabilities.json).

## 3. Repository selection

Репозиторий выбирается по месту ответственности артефакта, а не по удобству записи.

Receipt обязан содержать:

- выбранный repository;
- причину выбора;
- альтернативы, которые были исключены;
- пути в scope и вне scope.

## 4. Authority check

Разделяются:

```text
владелец аккаунта
≠ говорящий участник
≠ runtime
≠ инструмент
≠ task-specific authorization
```

До записи фиксируются:

- владелец аккаунта и репозитория;
- фактические repository permissions;
- откуда получено разрешение на эту задачу;
- выбранная write strategy.

По умолчанию:

```text
branch
→ draft PR
→ CI
→ review
→ отдельное merge authority
```

Прямая запись в default branch запрещена.

## 5. Source pin

До первого изменения закрепляются:

- default/base branch;
- exact base commit SHA;
- paths in scope;
- paths out of scope;
- известные связанные спецификации и их revisions.

Если base revision изменился до записи, операция останавливается или явно перебазируется с новым receipt.

## 6. Branch and change

Имя ветки: `agent/<bounded-description>`.

Каждое изменение должно иметь:

- адресуемый commit SHA;
- список изменённых путей;
- связь с `task_id`;
- отсутствие посторонних изменений.

В этой среде удалённые операции выполняются connector-first. Локальный `git/gh` является отдельным адаптером и не считается обязательным, когда GitHub App покрывает действие.

## 7. Checks

Запускаются наиболее релевантные доступные проверки:

- синтаксис и разбор данных;
- unit tests;
- существующий repository CI;
- проверки границ и запрещённых переходов;
- bounded examples.

Каждая проверка записывается как:

```text
name
command_or_job
status
observed_result
evidence
```

Невозможность запуска — `blocked` или `not_checked`, но не выдуманный `pass`.

## 8. BEC receipt

До открытия PR готовится execution receipt. Обязательные поля заданы в `GITHUB_OPERATIONAL_WORKFLOW.json` и в [`schemas/github-operation-receipt.schema.json`](schemas/github-operation-receipt.schema.json).

Главная граница:

```text
инструмент существует
≠ инструмент вызван
≠ внешний эффект произошёл
≠ внешний эффект проверен
```

Trust anchor для GitHub-операции — адресуемые GitHub objects: commit, PR, Actions run/job/log, review, merge commit или comment.

## 9. Pull request

PR открывается draft по умолчанию и содержит:

- что изменено;
- почему выбран этот repository;
- authority и write strategy;
- base revision и head revision;
- checks;
- BEC receipt;
- неизвестное;
- условия merge.

## 10. Review

Различаются:

- review не требовался;
- review запрошен и завершён;
- имеются unresolved required threads;
- review недоступен;
- merge отдельно разрешён владельцем задачи.

Необязательное отсутствие внешнего reviewer не превращается в фиктивное одобрение. В receipt указывается фактическое состояние.

## 11. Merge

Merge выполняется только при одновременном наличии:

- task-specific merge authority;
- exact expected head SHA;
- успешных required checks;
- отсутствия обязательных unresolved review threads.

Предпочтительный метод — squash, если repository допускает его и задача не требует сохранения отдельных commits.

## 12. Post-merge verification

После merge необходимо:

1. получить merge commit SHA;
2. перечитать изменённые файлы из default branch;
3. подтвердить, что PR закрыт как merged;
4. связать CI run с проверенным head SHA;
5. оставить финальный receipt в merged PR discussion или другом неизменяемом адресуемом месте.

Финальный comment применяется, чтобы записать merge SHA без рекурсивного PR только ради записи собственного merge.

## 13. CDTS handoff

Связываются адреса:

- task record;
- runtime/capability report;
- BEC receipt;
- PR;
- CI run;
- merge commit.

Связь не импортирует `world truth`, identity или причинность сверх evidence.

## 14. PCA handoff

PCA применяется только если операция содержит утверждение о продолжении процесса через смену модели, формы, runtime, host или корпуса.

Допустимые значения:

- `applicable` — создаётся отдельный transition record;
- `not_applicable` — утверждения о переходе не было;
- `unknown` — данных недостаточно.

Обычное продолжение одной GitHub-операции в одном ходе само по себе не доказывает identity continuity.

## 15. Closure

Операция закрыта только когда известны:

- merge или bounded non-merge outcome;
- итоговый receipt location;
- неизвестное;
- следующий адресуемый ход.

Состояния `blocked` и `aborted` являются полноценными результатами, если сохранены причина и evidence.
