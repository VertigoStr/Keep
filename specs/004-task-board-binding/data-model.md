# Data Model: Task to Board Binding

**Feature**: 004-task-board-binding
**Date**: 2026-03-02
**Database**: PostgreSQL

## Overview

Этот документ описывает модель данных для функциональности привязки задач к доскам. Модель включает расширение существующих сущностей Task и Board с добавлением связи между ними.

---

## Entity: Task (Modified)

### Description

Задача представляет единицу работы, которую нужно выполнить. Каждая задача принадлежит ровно одной доске.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Уникальный идентификатор задачи |
| `user_id` | Integer | NOT NULL, Foreign Key → users.id | Владелец задачи |
| `board_id` | Integer | NOT NULL, Foreign Key → boards.id | Идентификатор доски, к которой привязана задача |
| `title` | String(255) | NOT NULL | Название задачи |
| `description` | String(5000) | NOT NULL, Default: '' | Описание задачи |
| `due_date` | Date | NOT NULL | Срок выполнения задачи |
| `status` | String(50) | NOT NULL | Статус задачи |
| `created_at` | DateTime | NOT NULL, Default: UTC now | Дата и время создания задачи |
| `updated_at` | DateTime | NOT NULL, Default: UTC now | Дата и время последнего обновления |

### Constraints

- **Foreign Key**: `user_id` → `users.id` с CASCADE delete
- **Foreign Key**: `board_id` → `boards.id` с CASCADE delete
- **Unique Constraint**: Нет (задача может иметь любое сочетание полей)

### Relationships

| Relationship | Target Entity | Type | Description |
|--------------|---------------|------|-------------|
| `user` | User | Many-to-One | Владелец задачи |
| `board` | Board | Many-to-One | Доска, к которой привязана задача |

### Validation Rules

- `title`: минимум 1 символ, максимум 255 символов
- `description`: минимум 0 символов, максимум 5000 символов
- `due_date`: валидная дата в формате YYYY-MM-DD (прошедшие даты разрешены)
- `status`: должен быть одним из предопределенных значений
- `board_id`: должен ссылаться на существующую доску, принадлежащую тому же пользователю

### Status Values

```python
class TaskStatus(str, Enum):
    TODO = "к выполнению"
    IN_PROGRESS = "в работу"
    HAS_ISSUE = "возникла проблема"
    DONE = "сделано"
    CANCELLED = "отмена"
```

---

## Entity: Board (Modified)

### Description

Доска представляет собой контейнер для организации задач. Каждая доска принадлежит одному пользователю и содержит набор задач.

### Fields

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | Integer | Primary Key, Auto-increment | Уникальный идентификатор доски |
| `name` | String(255) | NOT NULL, Unique per user | Название доски |
| `user_id` | Integer | NOT NULL, Foreign Key → users.id | Идентификатор владельца доски |
| `is_default` | Boolean | NOT NULL, Default: False | Является ли доска по умолчанию |
| `created_at` | DateTime | NOT NULL, Default: UTC now | Дата и время создания доски |

### Constraints

- **Unique Constraint**: `(user_id, name)` - название доски должно быть уникальным в пределах одного пользователя
- **Unique Constraint**: `(user_id, is_default)` - у пользователя может быть только одна доска с `is_default=True`
- **Foreign Key**: `user_id` → `users.id` с CASCADE delete
- **Foreign Key**: `board_id` в Task → `boards.id` с CASCADE delete

### Relationships

| Relationship | Target Entity | Type | Description |
|--------------|---------------|------|-------------|
| `user` | User | Many-to-One | Владелец доски |
| `tasks` | Task | One-to-Many | Задачи на доске (cascade delete) |

### Validation Rules

- `name`: не может быть пустым, максимум 255 символов
- `name`: может содержать только буквы, цифры, пробелы и символы: `.,!?-:;`
- `is_default`: у пользователя может быть только одна доска с `is_default=True`

---

## Entity: User (Modified)

### Description

Существующая сущность пользователя. Добавлены связи с досками и задачами.

### New Relationships

| Relationship | Target Entity | Type | Description |
|--------------|---------------|------|-------------|
| `boards` | Board | One-to-Many | Доски пользователя (cascade delete) |
| `tasks` | Task | One-to-Many | Задачи пользователя (cascade delete) |

---

## Relationships Diagram

```
User (1) ────────< (N) Board
                      │
                      │ (1)
                      │
                      └───────< (N) Task
```

- Один пользователь может иметь много досок
- Одна доска принадлежит одному пользователю
- Одна доска может содержать много задач
- Одна задача принадлежит одной доске
- Cascade delete: при удалении пользователя удаляются все его доски и задачи
- Cascade delete: при удалении доски удаляются все её задачи

---

## Indexes

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| `tasks` | `idx_tasks_user_id` | B-Tree | Поиск задач пользователя |
| `tasks` | `idx_tasks_board_id` | B-Tree | Поиск задач на доске |
| `tasks` | `idx_tasks_status` | B-Tree | Фильтрация по статусу |
| `tasks` | `idx_tasks_due_date` | B-Tree | Фильтрация по сроку выполнения |
| `boards` | `idx_boards_user_id` | B-Tree | Поиск досок пользователя |
| `boards` | `idx_boards_user_default` | B-Tree | Поиск доски по умолчанию |

---

## Database Schema (SQL)

```sql
-- Tasks table (modified)
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    board_id INTEGER NOT NULL REFERENCES boards(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(5000) NOT NULL DEFAULT '',
    due_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_board_id ON tasks(board_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Boards table (modified)
CREATE TABLE boards (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    is_default BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, name),
    UNIQUE(user_id, is_default) WHERE is_default = TRUE
);

CREATE INDEX idx_boards_user_id ON boards(user_id);
CREATE INDEX idx_boards_user_default ON boards(user_id, is_default) WHERE is_default = TRUE;

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

---

## Data Access Patterns

### Task Repository

```python
class TaskRepository:
    def create_task(self, user_id: int, board_id: int, title: str,
                    description: str, due_date: date, status: str) -> Task
    def get_task_by_id(self, task_id: int) -> Optional[Task]
    def get_user_tasks(self, user_id: int) -> List[Task]
    def get_board_tasks(self, board_id: int) -> List[Task]
    def update_task(self, task_id: int, **kwargs) -> Optional[Task]
    def delete_task(self, task_id: int) -> bool
    def task_exists(self, task_id: int) -> bool
    def is_task_owner(self, task_id: int, user_id: int) -> bool
    def is_task_on_board(self, task_id: int, board_id: int) -> bool
```

### Board Repository

```python
class BoardRepository:
    def create_board(self, user_id: int, name: str, is_default: bool = False) -> Board
    def get_board_by_id(self, board_id: int) -> Optional[Board]
    def get_user_boards(self, user_id: int) -> List[Board]
    def get_default_board(self, user_id: int) -> Optional[Board]
    def update_board(self, board_id: int, **kwargs) -> Optional[Board]
    def delete_board(self, board_id: int) -> bool
    def board_exists(self, board_id: int) -> bool
    def is_board_owner(self, board_id: int, user_id: int) -> bool
    def set_default_board(self, user_id: int, board_id: int) -> bool
```

---

## Migration Strategy

### Alembic Migration

```python
# alembic/versions/003_add_board_id_to_tasks.py

def upgrade():
    # Добавляем поле board_id в таблицу tasks (nullable для обратной совместимости)
    op.add_column('tasks', sa.Column('board_id', sa.Integer(), nullable=True))

    # Создаем внешний ключ
    op.create_foreign_key(
        'fk_tasks_board_id',
        'tasks', 'boards',
        ['board_id'], ['id'],
        ondelete='CASCADE'
    )

    # Создаем индекс
    op.create_index('idx_tasks_board_id', 'tasks', ['board_id'])

    # Добавляем поле is_default в таблицу boards
    op.add_column('boards', sa.Column('is_default', sa.Boolean(), nullable=False, server_default='false'))

    # Создаем уникальный индекс для доски по умолчанию
    op.create_index(
        'idx_boards_user_default',
        'boards',
        ['user_id', 'is_default'],
        unique=True,
        postgresql_where=sa.text('is_default = TRUE')
    )

def downgrade():
    # Удаляем индексы и поля в обратном порядке
    op.drop_index('idx_boards_user_default', table_name='boards')
    op.drop_column('boards', 'is_default')
    op.drop_index('idx_tasks_board_id', table_name='tasks')
    op.drop_constraint('fk_tasks_board_id', 'tasks', type_='foreignkey')
    op.drop_column('tasks', 'board_id')
```

---

## State Transitions

### Task Status Transitions

```
Any status can transition to any other status (no restrictions)
```

### Board Default Status Transitions

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ┌──────────┐    set_default()    ┌──────────┐        │
│   │ is_default│ ──────────────────> │is_default│        │
│   │ = FALSE  │                     │ = TRUE   │        │
│   └──────────┘                     └──────────┘        │
│        ^                               │               │
│        │                               │               │
│        │         set_default()         │               │
│        └───────────────────────────────┘               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

- У пользователя может быть только одна доска с `is_default=True`
- При установке новой доски как по умолчанию, предыдущая доска автоматически сбрасывается

---

## Business Rules

1. **Автоматическая привязка**: При создании задачи без указания доски, задача привязывается к доске по умолчанию пользователя
2. **Создание доски по умолчанию**: Если у пользователя нет досок при создании первой задачи, автоматически создается доска по умолчанию
3. **Защита от чужих досок**: Пользователь не может привязать задачу к доске другого пользователя
4. **Каскадное удаление**: При удалении доски все её задачи удаляются
5. **Единственная доска по умолчанию**: У пользователя может быть только одна доска с `is_default=True`
6. **Обработка удаления доски по умолчанию**: При удалении доски по умолчанию автоматически назначается следующая доступная доска