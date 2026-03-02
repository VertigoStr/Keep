# API Contract: Task to Board Binding

**Feature**: 004-task-board-binding
**Date**: 2026-03-02
**API Version**: v1
**Base URL**: `/api/v1`

## Overview

Этот документ описывает API контракты для функциональности привязки задач к доскам. API следует RESTful принципам и использует JSON для обмена данными.

---

## Authentication

Все API endpoints требуют аутентификации через JWT токен в заголовке `Authorization`:

```
Authorization: Bearer <jwt_token>
```

---

## Common Response Codes

| Code | Description |
|------|-------------|
| `200` | Успешное выполнение запроса |
| `201` | Ресурс успешно создан |
| `400` | Неверный формат запроса |
| `401` | Не авторизован |
| `403` | Доступ запрещен |
| `404` | Ресурс не найден |
| `422` | Ошибка валидации данных |
| `500` | Внутренняя ошибка сервера |

---

## Common Error Response

```json
{
  "detail": "Error message description"
}
```

---

## Endpoints

### 1. Create Task with Board Binding

**Endpoint**: `POST /tasks`

**Description**: Создает новую задачу с автоматической или явной привязкой к доске.

**Request Body**:

```json
{
  "title": "Название задачи",
  "description": "Описание задачи",
  "due_date": "2026-03-15",
  "status": "к выполнению",
  "board_id": 123
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Название задачи (1-255 символов) |
| `description` | string | No | Описание задачи (0-5000 символов) |
| `due_date` | string (date) | Yes | Срок выполнения в формате YYYY-MM-DD |
| `status` | string | Yes | Статус задачи (см. TaskStatus) |
| `board_id` | integer | No | ID доски для привязки. Если не указан, используется доска по умолчанию |

**Success Response** (201):

```json
{
  "id": 456,
  "user_id": 1,
  "board_id": 123,
  "title": "Название задачи",
  "description": "Описание задачи",
  "due_date": "2026-03-15",
  "status": "к выполнению",
  "created_at": "2026-03-02T18:00:00Z",
  "updated_at": "2026-03-02T18:00:00Z"
}
```

**Error Responses**:

- `400`: Неверный формат даты
- `404`: Доска не найдена
- `403`: Доска принадлежит другому пользователю
- `422`: Ошибка валидации данных

---

### 2. Update Task Board Binding

**Endpoint**: `PUT /tasks/{task_id}`

**Description**: Обновляет задачу, включая возможность изменения привязки к доске.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | integer | Yes | ID задачи |

**Request Body**:

```json
{
  "title": "Обновленное название",
  "description": "Обновленное описание",
  "due_date": "2026-03-20",
  "status": "в работу",
  "board_id": 124
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | No | Название задачи |
| `description` | string | No | Описание задачи |
| `due_date` | string (date) | No | Срок выполнения |
| `status` | string | No | Статус задачи |
| `board_id` | integer | No | ID новой доски для привязки |

**Success Response** (200):

```json
{
  "id": 456,
  "user_id": 1,
  "board_id": 124,
  "title": "Обновленное название",
  "description": "Обновленное описание",
  "due_date": "2026-03-20",
  "status": "в работу",
  "created_at": "2026-03-02T18:00:00Z",
  "updated_at": "2026-03-02T18:30:00Z"
}
```

**Error Responses**:

- `404`: Задача или доска не найдена
- `403`: Задача принадлежит другому пользователю или доска принадлежит другому пользователю
- `422`: Ошибка валидации данных

---

### 3. Get Tasks by Board

**Endpoint**: `GET /boards/{board_id}/tasks`

**Description**: Возвращает все задачи, привязанные к указанной доске.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | integer | Yes | ID доски |

**Query Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `status` | string | No | Фильтрация по статусу |
| `limit` | integer | No | Максимальное количество результатов (default: 100) |
| `offset` | integer | No | Смещение для пагинации (default: 0) |

**Success Response** (200):

```json
{
  "tasks": [
    {
      "id": 456,
      "user_id": 1,
      "board_id": 123,
      "title": "Задача 1",
      "description": "Описание задачи 1",
      "due_date": "2026-03-15",
      "status": "к выполнению",
      "created_at": "2026-03-02T18:00:00Z",
      "updated_at": "2026-03-02T18:00:00Z"
    },
    {
      "id": 457,
      "user_id": 1,
      "board_id": 123,
      "title": "Задача 2",
      "description": "Описание задачи 2",
      "due_date": "2026-03-16",
      "status": "в работу",
      "created_at": "2026-03-02T18:05:00Z",
      "updated_at": "2026-03-02T18:10:00Z"
    }
  ],
  "total": 2,
  "limit": 100,
  "offset": 0
}
```

**Error Responses**:

- `404`: Доска не найдена
- `403`: Доска принадлежит другому пользователю

---

### 4. Get Task with Board Info

**Endpoint**: `GET /tasks/{task_id}`

**Description**: Возвращает задачу с информацией о привязанной доске.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `task_id` | integer | Yes | ID задачи |

**Success Response** (200):

```json
{
  "id": 456,
  "user_id": 1,
  "board_id": 123,
  "title": "Название задачи",
  "description": "Описание задачи",
  "due_date": "2026-03-15",
  "status": "к выполнению",
  "created_at": "2026-03-02T18:00:00Z",
  "updated_at": "2026-03-02T18:00:00Z",
  "board": {
    "id": 123,
    "name": "Моя доска",
    "user_id": 1,
    "is_default": true,
    "created_at": "2026-03-01T10:00:00Z"
  }
}
```

**Error Responses**:

- `404`: Задача не найдена
- `403`: Задача принадлежит другому пользователю

---

### 5. Create Board with Default Flag

**Endpoint**: `POST /boards`

**Description**: Создает новую доску с возможностью пометить её как доску по умолчанию.

**Request Body**:

```json
{
  "name": "Новая доска",
  "is_default": true
}
```

**Request Fields**:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Название доски (1-255 символов) |
| `is_default` | boolean | No | Является ли доска по умолчанию (default: false) |

**Success Response** (201):

```json
{
  "id": 123,
  "name": "Новая доска",
  "user_id": 1,
  "is_default": true,
  "created_at": "2026-03-02T18:00:00Z"
}
```

**Error Responses**:

- `400`: Название доски уже существует у пользователя
- `422`: Ошибка валидации данных

---

### 6. Set Default Board

**Endpoint**: `PUT /boards/{board_id}/set-default`

**Description**: Помечает указанную доску как доску по умолчанию для пользователя. Предыдущая доска по умолчанию автоматически сбрасывается.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | integer | Yes | ID доски |

**Success Response** (200):

```json
{
  "id": 123,
  "name": "Моя доска",
  "user_id": 1,
  "is_default": true,
  "created_at": "2026-03-01T10:00:00Z"
}
```

**Error Responses**:

- `404`: Доска не найдена
- `403`: Доска принадлежит другому пользователю

---

### 7. Get Default Board

**Endpoint**: `GET /boards/default`

**Description**: Возвращает доску по умолчанию для текущего пользователя.

**Success Response** (200):

```json
{
  "id": 123,
  "name": "Моя доска",
  "user_id": 1,
  "is_default": true,
  "created_at": "2026-03-01T10:00:00Z"
}
```

**Error Responses**:

- `404`: Доска по умолчанию не найдена

---

### 8. Delete Board

**Endpoint**: `DELETE /boards/{board_id}`

**Description**: Удаляет доску и все привязанные к ней задачи (каскадное удаление). Если удаляется доска по умолчанию, автоматически назначается следующая доступная доска.

**Path Parameters**:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `board_id` | integer | Yes | ID доски |

**Success Response** (200):

```json
{
  "message": "Board deleted successfully",
  "deleted_tasks_count": 5
}
```

**Error Responses**:

- `404`: Доска не найдена
- `403`: Доска принадлежит другому пользователю

---

## Enums

### TaskStatus

```json
{
  "values": [
    "к выполнению",
    "в работу",
    "возникла проблема",
    "сделано",
    "отмена"
  ]
}
```

---

## Data Models

### Task

```json
{
  "id": "integer",
  "user_id": "integer",
  "board_id": "integer",
  "title": "string (1-255)",
  "description": "string (0-5000)",
  "due_date": "string (date, YYYY-MM-DD)",
  "status": "string (TaskStatus)",
  "created_at": "string (datetime, ISO 8601)",
  "updated_at": "string (datetime, ISO 8601)"
}
```

### Board

```json
{
  "id": "integer",
  "name": "string (1-255)",
  "user_id": "integer",
  "is_default": "boolean",
  "created_at": "string (datetime, ISO 8601)"
}
```

### TaskListResponse

```json
{
  "tasks": "array[Task]",
  "total": "integer",
  "limit": "integer",
  "offset": "integer"
}
```

---

## Validation Rules

### Task Validation

- `title`: 1-255 символов, не может быть пустым
- `description`: 0-5000 символов
- `due_date`: валидная дата в формате YYYY-MM-DD
- `status`: должен быть одним из значений TaskStatus
- `board_id`: должен ссылаться на существующую доску, принадлежащую текущему пользователю

### Board Validation

- `name`: 1-255 символов, не может быть пустым, уникально в пределах пользователя
- `is_default`: у пользователя может быть только одна доска с `is_default=true`

---

## Rate Limiting

Все API endpoints имеют ограничение на количество запросов:

- `100 запросов в минуту` на пользователя

При превышении лимита возвращается код `429 Too Many Requests`.

---

## Versioning

API использует версионирование через URL path. Текущая версия: `v1`.

При изменении API в обратно несовместимом образом будет создана новая версия (`v2`).