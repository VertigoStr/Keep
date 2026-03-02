# API Contract: Board Management

**Feature**: 003-board-management
**Date**: 2026-03-02
**Version**: 1.0.0
**Base URL**: `http://localhost:8000/api/v1`

## Overview

Этот документ описывает REST API контракты для функциональности управления досками. API следует RESTful принципам и использует стандартные HTTP методы и коды статусов.

---

## Authentication

Все эндпоинты требуют аутентификации через JWT токен в заголовке `Authorization`:

```
Authorization: Bearer <jwt_token>
```

---

## Endpoints

### 1. Create Board

Создаёт новую доску для текущего пользователя с предопределёнными колонками.

**Endpoint**: `POST /boards`

**Request Headers**:
```
Content-Type: application/json
Authorization: Bearer <jwt_token>
```

**Request Body**:
```json
{
  "name": "Мой проект"
}
```

**Request Schema**:
| Field | Type | Required | Constraints | Description |
|-------|------|----------|-------------|-------------|
| `name` | string | Yes | 1-255 chars, regex: `^[\p{L}\p{N}\s.,!?\-:;]+$` | Название доски |

**Success Response**:
- **Code**: `201 Created`
- **Body**:
```json
{
  "id": 1,
  "name": "Мой проект",
  "user_id": 42,
  "created_at": "2026-03-02T17:00:00Z",
  "columns": [
    {
      "id": 1,
      "name": "К выполнению",
      "order": 1,
      "board_id": 1
    },
    {
      "id": 2,
      "name": "В работу",
      "order": 2,
      "board_id": 1
    },
    {
      "id": 3,
      "name": "Возникла проблема",
      "order": 3,
      "board_id": 1
    },
    {
      "id": 4,
      "name": "Сделано",
      "order": 4,
      "board_id": 1
    },
    {
      "id": 5,
      "name": "Отмена",
      "order": 5,
      "board_id": 1
    }
  ]
}
```

**Error Responses**:

| Code | Description | Body |
|------|-------------|------|
| `400 Bad Request` | Некорректные данные запроса | `{"detail": "Название обязательно"}` |
| `400 Bad Request` | Некорректные символы в названии | `{"detail": "Название может содержать только буквы, цифры, пробелы и символы .,!?-:;"}` |
| `409 Conflict` | Доска с таким названием уже существует | `{"detail": "Доска с таким названием уже существует"}` |
| `409 Conflict` | Лимит досок превышен | `{"detail": "Достигнут лимит досок (максимум 1)"}` |
| `401 Unauthorized` | Не авторизован | `{"detail": "Не авторизован"}` |

---

### 2. List Boards

Возвращает список всех досок текущего пользователя с количеством задач в каждой колонке.

**Endpoint**: `GET /boards`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Query Parameters**: None

**Success Response**:
- **Code**: `200 OK`
- **Body**:
```json
{
  "boards": [
    {
      "id": 1,
      "name": "Мой проект",
      "user_id": 42,
      "created_at": "2026-03-02T17:00:00Z",
      "columns": [
        {
          "id": 1,
          "name": "К выполнению",
          "order": 1,
          "task_count": 5
        },
        {
          "id": 2,
          "name": "В работу",
          "order": 2,
          "task_count": 3
        },
        {
          "id": 3,
          "name": "Возникла проблема",
          "order": 3,
          "task_count": 1
        },
        {
          "id": 4,
          "name": "Сделано",
          "order": 4,
          "task_count": 10
        },
        {
          "id": 5,
          "name": "Отмена",
          "order": 5,
          "task_count": 0
        }
      ]
    }
  ],
  "total": 1
}
```

**Empty Response**:
- **Code**: `200 OK`
- **Body**:
```json
{
  "boards": [],
  "total": 0,
  "message": "У вас пока нет досок"
}
```

**Error Responses**:

| Code | Description | Body |
|------|-------------|------|
| `401 Unauthorized` | Не авторизован | `{"detail": "Не авторизован"}` |

---

### 3. Get Board

Возвращает доску по ID с колонками и количеством задач.

**Endpoint**: `GET /boards/{id}`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | ID доски |

**Success Response**:
- **Code**: `200 OK`
- **Body**:
```json
{
  "id": 1,
  "name": "Мой проект",
  "user_id": 42,
  "created_at": "2026-03-02T17:00:00Z",
  "columns": [
    {
      "id": 1,
      "name": "К выполнению",
      "order": 1,
      "task_count": 5
    },
    {
      "id": 2,
      "name": "В работу",
      "order": 2,
      "task_count": 3
    },
    {
      "id": 3,
      "name": "Возникла проблема",
      "order": 3,
      "task_count": 1
    },
    {
      "id": 4,
      "name": "Сделано",
      "order": 4,
      "task_count": 10
    },
    {
      "id": 5,
      "name": "Отмена",
      "order": 5,
      "task_count": 0
    }
  ]
}
```

**Error Responses**:

| Code | Description | Body |
|------|-------------|------|
| `404 Not Found` | Доска не найдена | `{"detail": "Доска не найдена"}` |
| `403 Forbidden` | Нет прав на просмотр доски | `{"detail": "У вас нет прав на просмотр этой доски"}` |
| `401 Unauthorized` | Не авторизован | `{"detail": "Не авторизован"}` |

---

### 4. Delete Board

Удаляет доску и все связанные с ней колонки и задачи.

**Endpoint**: `DELETE /boards/{id}`

**Request Headers**:
```
Authorization: Bearer <jwt_token>
```

**Path Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `id` | integer | Yes | ID доски |

**Success Response**:
- **Code**: `204 No Content`
- **Body**: (empty)

**Error Responses**:

| Code | Description | Body |
|------|-------------|------|
| `404 Not Found` | Доска не найдена | `{"detail": "Доска не найдена"}` |
| `403 Forbidden` | Нет прав на удаление доски | `{"detail": "У вас нет прав на удаление этой доски"}` |
| `401 Unauthorized` | Не авторизован | `{"detail": "Не авторизован"}` |

---

## Data Schemas

### BoardCreate

```json
{
  "type": "object",
  "properties": {
    "name": {
      "type": "string",
      "minLength": 1,
      "maxLength": 255,
      "pattern": "^[\\p{L}\\p{N}\\s.,!?\\-:;]+$"
    }
  },
  "required": ["name"]
}
```

### BoardResponse

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"},
    "user_id": {"type": "integer"},
    "created_at": {"type": "string", "format": "date-time"},
    "columns": {
      "type": "array",
      "items": {"$ref": "#/definitions/ColumnResponse"}
    }
  }
}
```

### ColumnResponse

```json
{
  "type": "object",
  "properties": {
    "id": {"type": "integer"},
    "name": {"type": "string"},
    "order": {"type": "integer"},
    "board_id": {"type": "integer"},
    "task_count": {"type": "integer"}
  }
}
```

### BoardListResponse

```json
{
  "type": "object",
  "properties": {
    "boards": {
      "type": "array",
      "items": {"$ref": "#/definitions/BoardResponse"}
    },
    "total": {"type": "integer"},
    "message": {"type": "string"}
  }
}
```

---

## Error Response Schema

```json
{
  "type": "object",
  "properties": {
    "detail": {
      "type": "string",
      "description": "Человекочитаемое описание ошибки"
    }
  }
}
```

---

## HTTP Status Codes

| Code | Description |
|------|-------------|
| `200 OK` | Запрос выполнен успешно |
| `201 Created` | Ресурс успешно создан |
| `204 No Content` | Успешное удаление (без тела ответа) |
| `400 Bad Request` | Некорректные данные запроса |
| `401 Unauthorized` | Требуется аутентификация |
| `403 Forbidden` | Нет прав на выполнение операции |
| `404 Not Found` | Ресурс не найден |
| `409 Conflict` | Конфликт данных (дубликат, лимит превышен) |
| `422 Unprocessable Entity` | Ошибка валидации данных |
| `500 Internal Server Error` | Внутренняя ошибка сервера |

---

## Rate Limiting

API использует rate limiting для предотвращения злоупотреблений:

- **Limit**: 100 запросов в минуту на пользователя
- **Headers**:
  - `X-RateLimit-Limit`: Максимальное количество запросов
  - `X-RateLimit-Remaining`: Оставшееся количество запросов
  - `X-RateLimit-Reset`: Время сброса лимита (Unix timestamp)

При превышении лимита возвращается `429 Too Many Requests`.

---

## Versioning

API использует версионирование через URL path. Текущая версия: `v1`.

При внесении обратно несовместимых изменений будет создана новая версия (`v2`).

---

## OpenAPI Specification

API автоматически генерирует OpenAPI (Swagger) документацию, доступную по адресу:

```
http://localhost:8000/docs
```

Интерактивная документация ReDoc доступна по адресу:

```
http://localhost:8000/redoc