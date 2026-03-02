# Data Model: Board Management

**Feature**: 003-board-management
**Date**: 2026-03-02
**Status**: Complete

## Overview

Этот документ описывает модель данных для функциональности управления досками. Модель включает сущности Board (доска) и Column (колонка), а также их связи с существующими сущностями User и Task.

---

## Entity: Board

### Description

Доска представляет собой контейнер для организации задач. Каждая доска принадлежит одному пользователю и содержит набор предопределённых колонок.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Уникальный идентификатор доски |
| `name` | String(255) | NOT NULL, Unique per user | Название доски |
| `user_id` | Integer | NOT NULL, Foreign Key → users.id | Идентификатор владельца доски |
| `created_at` | DateTime | NOT NULL, Default: UTC now | Дата и время создания доски |

### Constraints

- **Unique Constraint**: `(user_id, name)` - название доски должно быть уникальным в пределах одного пользователя
- **Foreign Key**: `user_id` → `users.id` с CASCADE delete (при удалении пользователя удаляются все его доски)

### Relationships

| Relationship | Target Entity | Type | Description |
|--------------|---------------|------|-------------|
| `user` | User | Many-to-One | Владелец доски |
| `columns` | Column | One-to-Many | Колонки доски (cascade delete) |

### Validation Rules

- `name` не может быть пустым
- `name` максимум 255 символов
- `name` может содержать только буквы, цифры, пробелы и символы: `.,!?-:;`
- Пользователь может иметь максимум 1 доску

---

## Entity: Column

### Description

Колонка представляет собой статус задач в рамках доски. Колонки создаются автоматически при создании доски с предопределёнными названиями и порядком.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Уникальный идентификатор колонки |
| `name` | String(100) | NOT NULL | Название колонки |
| `order` | Integer | NOT NULL | Порядок отображения колонки (1-5) |
| `board_id` | Integer | NOT NULL, Foreign Key → boards.id | Идентификатор доски |

### Constraints

- **Foreign Key**: `board_id` → `boards.id` с CASCADE delete (при удалении доски удаляются все её колонки)

### Relationships

| Relationship | Target Entity | Type | Description |
|--------------|---------------|------|-------------|
| `board` | Board | Many-to-One | Доска, к которой принадлежит колонка |
| `tasks` | Task | One-to-Many | Задачи в колонке (cascade delete) |

### Validation Rules

- `name` не может быть пустым
- `order` должен быть в диапазоне 1-5
- Предопределённые названия колонок (в порядке):
  1. "К выполнению"
  2. "В работу"
  3. "Возникла проблема"
  4. "Сделано"
  5. "Отмена"

---

## Entity: User (Modified)

### Description

Существующая сущность пользователя. Добавлена связь с досками.

### New Relationships

| Relationship | Target Entity | Type | Description |
|--------------|---------------|------|-------------|
| `boards` | Board | One-to-Many | Доски пользователя (cascade delete) |

---

## Entity: Task (Modified)

### Description

Существующая сущность задачи (из 002-task-management). Добавлена связь с колонкой.

### New Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `column_id` | Integer | Nullable, Foreign Key → columns.id | Идентификатор колонки задачи |

### New Relationships

| Relationship | Target Entity | Type | Description |
|--------------|---------------|------|-------------|
| `column` | Column | Many-to-One | Колонка, в которой находится задача |

---

## Entity Relationship Diagram

```
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│    User     │ 1     * │   Board     │ 1     * │   Column    │
├─────────────┤─────────├─────────────┤─────────├─────────────┤
│ id          │         │ id          │         │ id          │
│ email       │         │ name        │         │ name        │
│ password    │         │ user_id     │         │ order       │
│ ...         │         │ created_at  │         │ board_id    │
└─────────────┘         └─────────────┘         └─────────────┘
                                                        │
                                                        │ 1
                                                        │
                                                        │ *
                                              ┌─────────────┐
                                              │    Task     │
                                              ├─────────────┤
                                              │ id          │
                                              │ title       │
                                              │ column_id   │
                                              │ ...         │
                                              └─────────────┘
```

---

## Database Schema

### Table: boards

```sql
CREATE TABLE boards (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_user_board_name UNIQUE (user_id, name)
);

CREATE INDEX idx_boards_user_id ON boards(user_id);
```

### Table: columns

```sql
CREATE TABLE columns (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    order INTEGER NOT NULL,
    board_id INTEGER NOT NULL REFERENCES boards(id) ON DELETE CASCADE
);

CREATE INDEX idx_columns_board_id ON columns(board_id);
CREATE UNIQUE INDEX uq_board_column_order ON columns(board_id, order);
```

### Table: users (modified)

```sql
-- Добавить индекс для оптимизации запросов досок пользователя
CREATE INDEX idx_users_boards ON users(id); -- уже существует как PK
```

### Table: tasks (modified)

```sql
-- Добавить колонку для связи с колонкой
ALTER TABLE tasks ADD COLUMN column_id INTEGER REFERENCES columns(id) ON DELETE SET NULL;

CREATE INDEX idx_tasks_column_id ON tasks(column_id);
```

---

## State Transitions

### Board Lifecycle

```
[Created] → [Active] → [Deleted]
    ↑           ↓
    └───────────┘
```

- **Created**: Доска создана с предопределёнными колонками
- **Active**: Доска используется для управления задачами
- **Deleted**: Доска удалена вместе со всеми колонками и задачами (hard delete)

### Column Lifecycle

Колонки создаются автоматически при создании доски и удаляются только при удалении доски. Ручное управление колонками не предусмотрено в рамках этой функции.

---

## Data Integrity Rules

1. **Board ownership**: Доска может принадлежать только одному пользователю
2. **Board name uniqueness**: Название доски должно быть уникальным в пределах одного пользователя
3. **Board limit**: Пользователь может иметь максимум 1 доску
4. **Column predefined**: Колонки создаются автоматически с предопределёнными названиями и порядком
5. **Cascade deletion**: При удалении доски удаляются все её колонки и задачи
6. **Task-column relationship**: Задача может быть связана только с одной колонкой

---

## Migration Notes

Для внедрения этой модели данных потребуется:

1. Создать таблицу `boards`
2. Создать таблицу `columns`
3. Добавить колонку `column_id` в таблицу `tasks`
4. Добавить связь `boards` в модель `User`
5. Создать индексы для оптимизации запросов

Миграция будет выполнена через Alembic.