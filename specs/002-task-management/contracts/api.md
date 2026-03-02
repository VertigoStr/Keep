# API Contract: Task Management

**Feature**: 002-task-management
**Date**: 2026-03-02
**Protocol**: HTTP/REST
**Content-Type**: application/json

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All task endpoints require authentication via JWT token in HTTP-only cookie.

## Endpoints

### POST /tasks

Create a new task for the authenticated user.

**Request**:
```http
POST /api/v1/tasks
Content-Type: application/json
Cookie: session_token=<jwt_token>
```

**Request Body**:
```json
{
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
  "due_date": "2026-03-15",
  "status": "к выполнению"
}
```

**Request Validation**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | string | Yes | Min 1 char, max 255 chars |
| description | string | No | Max 5000 chars, defaults to empty string |
| due_date | string (date) | Yes | Valid date in YYYY-MM-DD format |
| status | string | Yes | Must be one of: "к выполнению", "в работу", "возникла проблема", "сделано", "отмена" |

**Response (201 Created)**:
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
  "due_date": "2026-03-15",
  "status": "к выполнению",
  "created_at": "2026-03-02T10:00:00Z",
  "updated_at": "2026-03-02T10:00:00Z"
}
```

**Response (400 Bad Request)** - Validation errors:
```json
{
  "error": "validation_error",
  "message": "Title is required",
  "details": {
    "field": "title",
    "constraint": "minimum 1 character"
  }
}
```

**Response (400 Bad Request)** - Description too long:
```json
{
  "error": "validation_error",
  "message": "Description exceeds maximum length",
  "details": {
    "field": "description",
    "constraint": "maximum 5000 characters"
  }
}
```

**Response (400 Bad Request)** - Invalid date format:
```json
{
  "error": "validation_error",
  "message": "Invalid date format. Use YYYY-MM-DD",
  "details": {
    "field": "due_date",
    "constraint": "valid date in YYYY-MM-DD format"
  }
}
```

**Response (400 Bad Request)** - Invalid status:
```json
{
  "error": "validation_error",
  "message": "Invalid status value",
  "details": {
    "field": "status",
    "constraint": "must be one of: к выполнению, в работу, возникла проблема, сделано, отмена"
  }
}
```

**Response (401 Unauthorized)** - Not authenticated:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

---

### GET /tasks

Get all tasks for the authenticated user.

**Request**:
```http
GET /api/v1/tasks
Cookie: session_token=<jwt_token>
```

**Response (200 OK)**:
```json
{
  "tasks": [
    {
      "id": 1,
      "title": "Complete project documentation",
      "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
      "due_date": "2026-03-15",
      "status": "к выполнению",
      "created_at": "2026-03-02T10:00:00Z",
      "updated_at": "2026-03-02T10:00:00Z"
    },
    {
      "id": 2,
      "title": "Fix login bug",
      "description": "Users cannot login with special characters in password",
      "due_date": "2026-03-10",
      "status": "в работу",
      "created_at": "2026-03-01T15:30:00Z",
      "updated_at": "2026-03-02T09:00:00Z"
    }
  ]
}
```

**Response (200 OK)** - Empty list:
```json
{
  "tasks": []
}
```

**Response (401 Unauthorized)** - Not authenticated:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

---

### GET /tasks/{task_id}

Get a specific task by ID.

**Request**:
```http
GET /api/v1/tasks/1
Cookie: session_token=<jwt_token>
```

**Response (200 OK)**:
```json
{
  "id": 1,
  "title": "Complete project documentation",
  "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
  "due_date": "2026-03-15",
  "status": "к выполнению",
  "created_at": "2026-03-02T10:00:00Z",
  "updated_at": "2026-03-02T10:00:00Z"
}
```

**Response (401 Unauthorized)** - Not authenticated:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

**Response (403 Forbidden)** - Not task owner:
```json
{
  "error": "forbidden",
  "message": "You do not have permission to access this task"
}
```

**Response (404 Not Found)** - Task not found:
```json
{
  "error": "not_found",
  "message": "Task not found"
}
```

---

### PUT /tasks/{task_id}

Update a specific task.

**Request**:
```http
PUT /api/v1/tasks/1
Content-Type: application/json
Cookie: session_token=<jwt_token>
```

**Request Body** (all fields optional):
```json
{
  "title": "Complete project documentation (updated)",
  "description": "Write comprehensive documentation for the new feature including API reference and user guide. Add examples.",
  "due_date": "2026-03-20",
  "status": "в работу"
}
```

**Request Validation**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| title | string | No | Min 1 char, max 255 chars (if provided) |
| description | string | No | Max 5000 chars (if provided) |
| due_date | string (date) | No | Valid date in YYYY-MM-DD format (if provided) |
| status | string | No | Must be one of: "к выполнению", "в работу", "возникла проблема", "сделано", "отмена" (if provided) |

**Response (200 OK)**:
```json
{
  "id": 1,
  "title": "Complete project documentation (updated)",
  "description": "Write comprehensive documentation for the new feature including API reference and user guide. Add examples.",
  "due_date": "2026-03-20",
  "status": "в работу",
  "created_at": "2026-03-02T10:00:00Z",
  "updated_at": "2026-03-02T11:00:00Z"
}
```

**Response (400 Bad Request)** - Validation errors:
```json
{
  "error": "validation_error",
  "message": "Invalid status value",
  "details": {
    "field": "status",
    "constraint": "must be one of: к выполнению, в работу, возникла проблема, сделано, отмена"
  }
}
```

**Response (401 Unauthorized)** - Not authenticated:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

**Response (403 Forbidden)** - Not task owner:
```json
{
  "error": "forbidden",
  "message": "You do not have permission to modify this task"
}
```

**Response (404 Not Found)** - Task not found:
```json
{
  "error": "not_found",
  "message": "Task not found"
}
```

---

### DELETE /tasks/{task_id}

Delete a specific task.

**Request**:
```http
DELETE /api/v1/tasks/1
Cookie: session_token=<jwt_token>
```

**Response (200 OK)**:
```json
{
  "message": "Task deleted successfully"
}
```

**Response (401 Unauthorized)** - Not authenticated:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

**Response (403 Forbidden)** - Not task owner:
```json
{
  "error": "forbidden",
  "message": "You do not have permission to delete this task"
}
```

**Response (404 Not Found)** - Task not found:
```json
{
  "error": "not_found",
  "message": "Task not found"
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "field": "field_name",
    "constraint": "constraint_description"
  }
}
```

**Error Codes**:
- `validation_error` - Request validation failed
- `unauthorized` - Authentication required or invalid
- `forbidden` - User does not have permission
- `not_found` - Resource not found

## Status Values

Valid task status values:
- `к выполнению` - To do
- `в работу` - In progress
- `возникла проблема` - Has issue
- `сделано` - Done
- `отмена` - Cancelled

## Date Format

All dates use ISO 8601 format:
- Request: `YYYY-MM-DD` (e.g., `2026-03-15`)
- Response: `YYYY-MM-DDTHH:MM:SSZ` (e.g., `2026-03-02T10:00:00Z`)

## Rate Limiting

No rate limiting is currently applied to task endpoints beyond the authentication rate limiting.

## Pagination

Task listing endpoint does not currently support pagination. All tasks for the user are returned in a single response. Future versions may add pagination for large task lists.