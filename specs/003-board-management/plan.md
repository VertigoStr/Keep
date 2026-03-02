# Implementation Plan: Board Management

**Branch**: `003-board-management` | **Date**: 2026-03-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-board-management/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Реализовать функциональность управления досками для системы управления задачами. Пользователи могут создавать доски с предопределёнными колонками ("К выполнению", "В работу", "Возникла проблема", "Сделано", "Отмена"), просматривать список своих досок и удалять доски. Каждая доска принадлежит одному пользователю, лимит - 1 доска на пользователя. Технический подход: REST API на FastAPI с SQLAlchemy ORM для работы с PostgreSQL, каскадное удаление связанных данных.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic, Alembic
**Storage**: PostgreSQL
**Testing**: pytest, pytest-asyncio, httpx
**Target Platform**: Linux server
**Project Type**: web-service
**Performance Goals**: <1s для загрузки списка досок, <2s для удаления доски
**Constraints**: 1 доска на пользователя, max 255 символов для названия доски, разрешённые символы: буквы, цифры, пробелы и базовая пунктуация (.,!?-:;)
**Scale/Scope**: Часть системы управления задачами, интеграция с существующими функциями аутентификации и управления задачами

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Python 3.11 | ✅ PASS | Язык соответствует конституции |
| FastAPI | ✅ PASS | Framework соответствует конституции |
| PEP8 compliance | ✅ PASS | Будет обеспечен через pre-commit hooks |
| SOLID, DRY, KISS | ✅ PASS | Архитектура следует этим принципам |
| snake_case naming | ✅ PASS | Будет применяться во всём коде |
| Max 120 char lines | ✅ PASS | Будет обеспечен через линтеры |
| Documentation | ✅ PASS | Все методы и классы будут документированы |
| Unit tests | ✅ PASS | Будут написаны для всей функциональности |
| 80% test coverage | ✅ PASS | Целевое покрытие будет достигнуто |
| Secrets in env vars | ✅ PASS | Секреты хранятся в .env |
| One commit = one task | ✅ PASS | Будет соблюдаться при коммитах |

**GATE RESULT**: ✅ PASS - All constitution requirements satisfied. Proceeding to Phase 0.

## Project Structure

### Documentation (this feature)

```text
specs/003-board-management/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.md
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── models/
│   ├── __init__.py
│   ├── user.py          # Существующий
│   ├── board.py         # Новый: модель доски
│   └── column.py        # Новый: модель колонки
├── schemas/
│   ├── __init__.py
│   ├── auth.py          # Существующий
│   └── board.py         # Новый: Pydantic схемы для досок
├── services/
│   ├── __init__.py
│   ├── auth_service.py  # Существующий
│   └── board_service.py # Новый: бизнес-логика управления досками
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py    # Существующий
│   ├── board_repository.py   # Новый: доступ к данным досок
│   └── column_repository.py  # Новый: доступ к данным колонок
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── auth.py      # Существующий
│       └── boards.py    # Новый: API эндпоинты для досок
└── utils/
    ├── __init__.py
    ├── validators.py    # Существующий
    └── board_validators.py  # Новый: валидаторы для досок

tests/
├── unit/
│   ├── test_board_service.py      # Новый
│   ├── test_board_repository.py   # Новый
│   └── test_board_validators.py   # Новый
├── integration/
│   └── test_board_api.py          # Новый
└── contract/
    └── test_board_api.py          # Новый
```

**Structure Decision**: Выбрана структура "Single project" (Option 1), соответствующая существующей архитектуре проекта. Новые модули добавляются в существующие директории (models, schemas, services, repositories, api/v1, utils) для поддержания согласованности с кодовой базой. Тесты следуют той же структуре с разделением на unit, integration и contract тесты.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

**No violations detected.** All design decisions align with constitution principles.
