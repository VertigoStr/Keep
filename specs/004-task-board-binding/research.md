# Research: Task to Board Binding

**Feature**: 004-task-board-binding
**Date**: 2026-03-02
**Status**: Complete

## Overview

Этот документ содержит результаты исследования для реализации функциональности привязки задач к доскам пользователя. Все неопределенности из спецификации были разрешены.

---

## Research Findings

### 1. Модель отношений между задачами и досками

**Decision**: Одна задача принадлежит только одной доске (отношение один-ко-многим: Board → Task)

**Rationale**:
- Упрощает модель данных и запросы к базе данных
- Соответствует паттерну Trello/Kanban, где задача находится в одной колонке одной доски
- Упрощает каскадное удаление задач при удалении доски

**Alternatives considered**:
- Много-ко-многим: Отклонено из-за избыточной сложности для текущих требований
- Одна задача может быть на нескольких досках: Отклонено - не соответствует требованиям спецификации

---

### 2. Каскадное удаление задач при удалении доски

**Decision**: Использовать CASCADE DELETE на уровне базы данных

**Rationale**:
- Гарантирует целостность данных на уровне БД
- Упрощает логику приложения - не нужно вручную удалять задачи
- SQLAlchemy поддерживает CASCADE DELETE через relationship

**Implementation**:
```python
# В модели Board
tasks = relationship("Task", back_populates="board", cascade="all, delete-orphan")

# В модели Task
board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"))
```

**Alternatives considered**:
- Мягкое удаление (soft delete): Отклонено - не соответствует требованиям спецификации
- Ручное удаление в сервисе: Отклонено - менее надежно, возможны утечки данных

---

### 3. Определение доски по умолчанию для пользователя

**Decision**: Пользователь явно помечает одну из своих досок как "по умолчанию"

**Rationale**:
- Дает пользователю контроль над организацией задач
- Позволяет менять доску по умолчанию без изменения всех задач
- Соответствует требованиям спецификации (FR-001)

**Implementation**:
- Добавить поле `is_default` в модель Board (boolean, default=False)
- Обеспечить, что у пользователя может быть только одна доска с `is_default=True`
- При создании первой доски автоматически устанавливать `is_default=True`

**Alternatives considered**:
- Первая созданная доска всегда по умолчанию: Отклонено - менее гибко
- Нет доски по умолчанию, всегда явное указание: Отклонено - снижает удобство использования

---

### 4. Обработка ситуации при отсутствии досок у пользователя

**Decision**: Автоматически создавать доску по умолчанию при создании первой задачи

**Rationale**:
- Соответствует требованию FR-004 спецификации
- Обеспечивает плавный onboarding для новых пользователей
- Предотвращает ошибки при создании задачи

**Implementation**:
```python
# В TaskService.create_task()
if not board_id:
    board = board_repository.get_default_board(user_id)
    if not board:
        board = board_service.create_default_board(user_id)
    board_id = board.id
```

**Alternatives considered**:
- Возвращать ошибку: Отклонено - снижает удобство использования
- Требовать явного создания доски: Отклонено - увеличивает friction для пользователя

---

### 5. Защита от привязки задач к чужим доскам

**Decision**: Проверка владения доской на уровне сервиса

**Rationale**:
- Обеспечивает безопасность данных
- Соответствует требованию FR-006 спецификации
- Позволяет вернуть понятное сообщение об ошибке

**Implementation**:
```python
# В TaskService.create_task() и update_task()
if board_id:
    board = board_repository.get_by_id(board_id)
    if not board or board.user_id != user_id:
        raise PermissionError("Board not found or access denied")
```

**Alternatives considered**:
- Проверка на уровне БД (ROW LEVEL SECURITY): Отклонено - избыточно для текущих требований
- Проверка на уровне API middleware: Отклонено - менее специфично для бизнес-логики

---

### 6. Обработка удаления доски по умолчанию

**Decision**: При удалении доски по умолчанию автоматически назначать следующую доступную доску

**Rationale**:
- Соответствует требованию FR-009 спецификации
- Предотвращает ситуацию, когда у пользователя нет доски по умолчанию
- Обеспечивает непрерывность работы пользователя

**Implementation**:
```python
# В BoardService.delete_board()
if board.is_default:
    remaining_boards = board_repository.get_user_boards(user_id)
    if remaining_boards:
        remaining_boards[0].is_default = True
```

**Alternatives considered**:
- Оставлять без доски по умолчанию: Отклонено - нарушает инвариант системы
- Создавать новую доску по умолчанию: Отклонено - может быть неожиданным для пользователя

---

### 7. Просмотр задач в контексте доски

**Decision**: Добавить endpoint для получения задач по board_id

**Rationale**:
- Соответствует требованию FR-008 спецификации
- Позволяет фильтровать задачи по доске
- Оптимизирует запросы к базе данных

**Implementation**:
```python
# В TaskRepository
def get_tasks_by_board(board_id: int) -> List[Task]:
    return session.query(Task).filter(Task.board_id == board_id).all()

# В API
@router.get("/boards/{board_id}/tasks")
async def get_board_tasks(board_id: int, current_user: User = Depends(get_current_user)):
    # Проверка владения доской
    # Возврат задач
```

**Alternatives considered**:
- Фильтрация на клиенте: Отклонено - неэффективно для больших объемов данных
- Отдельный endpoint для каждой доски: Отклонено - избыточно

---

### 8. Миграция базы данных

**Decision**: Использовать Alembic для создания миграции

**Rationale**:
- Alembic уже используется в проекте
- Позволяет версионировать изменения схемы БД
- Поддерживает откаты миграций

**Implementation**:
```bash
alembic revision --autogenerate -m "Add board_id to tasks table"
```

**Migration steps**:
1. Добавить поле `board_id` в таблицу `tasks` (nullable для обратной совместимости)
2. Добавить внешний ключ `tasks.board_id → boards.id` с CASCADE DELETE
3. Создать индекс на `tasks.board_id` для оптимизации запросов
4. Обновить модели SQLAlchemy

**Alternatives considered**:
- Ручное выполнение SQL: Отклонено - менее надежно, не версионировано
- Использование других инструментов миграции: Отклонено - Alembic уже интегрирован

---

### 9. Производительность

**Decision**: Оптимизировать запросы с помощью индексов и eager loading

**Rationale**:
- Соответствует требованию NFR-002 (<2s для загрузки до 1000 задач)
- SQLAlchemy поддерживает eager loading через `joinedload` и `selectinload`

**Implementation**:
```python
# Индексы
CREATE INDEX idx_tasks_board_id ON tasks(board_id);

# Eager loading
tasks = session.query(Task).options(
    joinedload(Task.board)
).filter(Task.board_id == board_id).all()
```

**Alternatives considered**:
- Кэширование на уровне приложения: Отклонено - избыточно для текущих требований
- Пагинация: Будет добавлена в будущем при необходимости

---

### 10. Тестирование

**Decision**: Использовать pytest с pytest-asyncio для тестирования

**Rationale**:
- pytest уже используется в проекте
- pytest-asyncio поддерживает асинхронные тесты FastAPI
- httpx позволяет тестировать API endpoints

**Test coverage**:
- Unit тесты для сервисов и репозиториев
- Integration тесты для сценариев привязки задач к доскам
- Contract тесты для API endpoints

**Alternatives considered**:
- Использование других фреймворков тестирования: Отклонено - pytest уже интегрирован
- Только ручное тестирование: Отклонено - не соответствует конституции (80% покрытие)

---

## Summary

Все неопределенности из спецификации были разрешены. Основные решения:

1. **Отношение**: Board (1) → Task (N) с CASCADE DELETE
2. **Доска по умолчанию**: Явное помечение пользователем, автоматическое создание при необходимости
3. **Безопасность**: Проверка владения доской на уровне сервиса
4. **Миграция**: Alembic с добавлением `board_id` в таблицу `tasks`
5. **Производительность**: Индексы и eager loading
6. **Тестирование**: pytest с pytest-asyncio и httpx

Все решения соответствуют конституции проекта (Python 3.11, FastAPI, PEP8, SOLID, 80% покрытие тестами).