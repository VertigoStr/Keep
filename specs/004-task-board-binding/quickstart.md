# Quickstart: Task to Board Binding

**Feature**: 004-task-board-binding
**Date**: 2026-03-02

## Overview

Этот документ предоставляет краткое руководство по использованию функциональности привязки задач к доскам.

---

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Установленные зависимости (см. `requirements.txt`)
- Выполненные миграции базы данных

---

## Setup

### 1. Apply Database Migration

```bash
# Создать миграцию
alembic revision --autogenerate -m "Add board_id to tasks table"

# Применить миграцию
alembic upgrade head
```

### 2. Start the Application

```bash
# Активировать виртуальное окружение
source venv/bin/activate  # На Windows: venv\Scripts\activate

# Запустить сервер
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

API будет доступен по адресу: `http://localhost:8000`

---

## Authentication

Все API endpoints требуют аутентификации. Сначала получите JWT токен:

```bash
# Регистрация
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'

# Вход
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }'
```

Сохраните полученный `access_token` для использования в последующих запросах.

---

## Common Use Cases

### 1. Create a Task with Automatic Board Binding

Если у пользователя уже есть доска по умолчанию, задача автоматически привяжется к ней:

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новая задача",
    "description": "Описание задачи",
    "due_date": "2026-03-15",
    "status": "к выполнению"
  }'
```

**Response**:
```json
{
  "id": 1,
  "user_id": 1,
  "board_id": 1,
  "title": "Новая задача",
  "description": "Описание задачи",
  "due_date": "2026-03-15",
  "status": "к выполнению",
  "created_at": "2026-03-02T18:00:00Z",
  "updated_at": "2026-03-02T18:00:00Z"
}
```

### 2. Create a Task with Explicit Board

Укажите конкретную доску при создании задачи:

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Задача на конкретной доске",
    "description": "Описание",
    "due_date": "2026-03-20",
    "status": "к выполнению",
    "board_id": 2
  }'
```

### 3. Create a Board

Создайте новую доску:

```bash
curl -X POST http://localhost:8000/api/v1/boards \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Проект Alpha",
    "is_default": true
  }'
```

**Response**:
```json
{
  "id": 2,
  "name": "Проект Alpha",
  "user_id": 1,
  "is_default": true,
  "created_at": "2026-03-02T18:00:00Z"
}
```

### 4. Get Tasks on a Board

Получите все задачи на конкретной доске:

```bash
curl -X GET http://localhost:8000/api/v1/boards/1/tasks \
  -H "Authorization: Bearer <access_token>"
```

**Response**:
```json
{
  "tasks": [
    {
      "id": 1,
      "user_id": 1,
      "board_id": 1,
      "title": "Новая задача",
      "description": "Описание задачи",
      "due_date": "2026-03-15",
      "status": "к выполнению",
      "created_at": "2026-03-02T18:00:00Z",
      "updated_at": "2026-03-02T18:00:00Z"
    }
  ],
  "total": 1,
  "limit": 100,
  "offset": 0
}
```

### 5. Update Task Board

Переместите задачу на другую доску:

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "board_id": 2
  }'
```

### 6. Set Default Board

Пометьте доску как доску по умолчанию:

```bash
curl -X PUT http://localhost:8000/api/v1/boards/2/set-default \
  -H "Authorization: Bearer <access_token>"
```

### 7. Get Default Board

Получите доску по умолчанию:

```bash
curl -X GET http://localhost:8000/api/v1/boards/default \
  -H "Authorization: Bearer <access_token>"
```

### 8. Delete a Board

Удалите доску (все задачи на доске будут удалены каскадно):

```bash
curl -X DELETE http://localhost:8000/api/v1/boards/2 \
  -H "Authorization: Bearer <access_token>"
```

**Response**:
```json
{
  "message": "Board deleted successfully",
  "deleted_tasks_count": 3
}
```

---

## Task Status Values

Допустимые значения статуса задачи:

- `к выполнению` - задача запланирована
- `в работу` - задача в процессе выполнения
- `возникла проблема` - возникли проблемы с выполнением
- `сделано` - задача завершена
- `отмена` - задача отменена

---

## Error Handling

### Common Errors

**404 Not Found** - Ресурс не найден:
```json
{
  "detail": "Board not found"
}
```

**403 Forbidden** - Доступ запрещен:
```json
{
  "detail": "You don't have permission to access this board"
}
```

**422 Validation Error** - Ошибка валидации:
```json
{
  "detail": [
    {
      "loc": ["body", "title"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

---

## Testing

### Run Tests

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=src --cov-report=html

# Конкретный файл
pytest tests/integration/test_task_board_binding.py
```

### Test Coverage Target

- Минимальное покрытие: **80%**
- Unit тесты: сервисы и репозитории
- Integration тесты: сценарии привязки задач к доскам
- Contract тесты: API endpoints

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b 004-task-board-binding
```

### 2. Implement Changes

- Обновите модели в `src/models/task.py` и `src/models/board.py`
- Обновите схемы в `src/schemas/task.py` и `src/schemas/board.py`
- Обновите сервисы в `src/services/task_service.py` и `src/services/board_service.py`
- Обновите репозитории в `src/repositories/task_repository.py` и `src/repositories/board_repository.py`
- Обновите API endpoints в `src/api/v1/tasks.py` и `src/api/v1/boards.py`

### 3. Create Migration

```bash
alembic revision --autogenerate -m "Add board_id to tasks table"
```

### 4. Apply Migration

```bash
alembic upgrade head
```

### 5. Run Tests

```bash
pytest --cov=src --cov-report=html
```

### 6. Commit Changes

```bash
git add .
git commit -m "feat: add task to board binding"
```

---

## API Documentation

Интерактивная документация API доступна по адресу:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Troubleshooting

### Migration Issues

Если миграция не применяется:

```bash
# Проверить текущую версию
alembic current

# Проверить историю миграций
alembic history

# Откатить миграцию
alembic downgrade -1
```

### Database Connection Issues

Проверьте настройки в `.env`:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```

### Test Failures

Убедитесь, что тестовая база данных настроена:

```env
TEST_DATABASE_URL=postgresql://user:password@localhost:5432/test_dbname
```

---

## Next Steps

- Изучите полную спецификацию: [`spec.md`](./spec.md)
- Изучите модель данных: [`data-model.md`](./data-model.md)
- Изучите API контракты: [`contracts/api.md`](./contracts/api.md)
- Изучите результаты исследования: [`research.md`](./research.md)