# Quickstart: Board Management

**Feature**: 003-board-management
**Date**: 2026-03-02

## Overview

Этот документ содержит краткое руководство по началу работы с функциональностью управления досками. Он описывает основные шаги для запуска, тестирования и использования API.

---

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip (Python package manager)
- git

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd trello/src
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env with your database credentials
```

Required environment variables:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/trello
SECRET_KEY=your-secret-key
```

### 5. Run database migrations

```bash
alembic upgrade head
```

---

## Running the Application

### Development server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Quick Test

### 1. Register a user

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "id": 1,
  "email": "test@example.com",
  "created_at": "2026-03-02T17:00:00Z"
}
```

### 2. Login to get JWT token

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

Save the `access_token` for subsequent requests.

### 3. Create a board

```bash
curl -X POST http://localhost:8000/api/v1/boards \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-access-token>" \
  -d '{
    "name": "Мой проект"
  }'
```

Response:
```json
{
  "id": 1,
  "name": "Мой проект",
  "user_id": 1,
  "created_at": "2026-03-02T17:00:00Z",
  "columns": [
    {"id": 1, "name": "К выполнению", "order": 1, "board_id": 1},
    {"id": 2, "name": "В работу", "order": 2, "board_id": 1},
    {"id": 3, "name": "Возникла проблема", "order": 3, "board_id": 1},
    {"id": 4, "name": "Сделано", "order": 4, "board_id": 1},
    {"id": 5, "name": "Отмена", "order": 5, "board_id": 1}
  ]
}
```

### 4. List boards

```bash
curl -X GET http://localhost:8000/api/v1/boards \
  -H "Authorization: Bearer <your-access-token>"
```

Response:
```json
{
  "boards": [
    {
      "id": 1,
      "name": "Мой проект",
      "user_id": 1,
      "created_at": "2026-03-02T17:00:00Z",
      "columns": [
        {"id": 1, "name": "К выполнению", "order": 1, "task_count": 0},
        {"id": 2, "name": "В работу", "order": 2, "task_count": 0},
        {"id": 3, "name": "Возникла проблема", "order": 3, "task_count": 0},
        {"id": 4, "name": "Сделано", "order": 4, "task_count": 0},
        {"id": 5, "name": "Отмена", "order": 5, "task_count": 0}
      ]
    }
  ],
  "total": 1
}
```

### 5. Get a specific board

```bash
curl -X GET http://localhost:8000/api/v1/boards/1 \
  -H "Authorization: Bearer <your-access-token>"
```

### 6. Delete a board

```bash
curl -X DELETE http://localhost:8000/api/v1/boards/1 \
  -H "Authorization: Bearer <your-access-token>"
```

Response: `204 No Content` (empty body)

---

## Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=src --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

### Run specific test file

```bash
pytest tests/unit/test_board_service.py
```

### Run integration tests

```bash
pytest tests/integration/test_board_api.py
```

### Run contract tests

```bash
pytest tests/contract/test_board_api.py
```

---

## Project Structure

```
src/
├── models/
│   ├── board.py          # Board model
│   └── column.py         # Column model
├── schemas/
│   └── board.py          # Pydantic schemas
├── services/
│   └── board_service.py  # Business logic
├── repositories/
│   ├── board_repository.py   # Data access for boards
│   └── column_repository.py  # Data access for columns
├── api/v1/
│   └── boards.py         # API endpoints
└── utils/
    └── board_validators.py   # Validation helpers
```

---

## Common Errors

### Board name validation error

```json
{
  "detail": "Название может содержать только буквы, цифры, пробелы и символы .,!?-:;"
}
```

**Solution**: Use only allowed characters in board name.

### Board already exists

```json
{
  "detail": "Доска с таким названием уже существует"
}
```

**Solution**: Use a different name for the board.

### Board limit exceeded

```json
{
  "detail": "Достигнут лимит досок (максимум 1)"
}
```

**Solution**: Delete existing board before creating a new one.

### Unauthorized

```json
{
  "detail": "Не авторизован"
}
```

**Solution**: Include valid JWT token in Authorization header.

---

## Development Tips

### Create a new migration

```bash
alembic revision --autogenerate -m "Add boards and columns tables"
```

### Rollback migration

```bash
alembic downgrade -1
```

### Check database schema

```bash
alembic history
```

### Format code

```bash
black src/ tests/
```

### Run linter

```bash
flake8 src/ tests/
```

---

## Next Steps

- Read the [API Contract](./contracts/api.md) for detailed API documentation
- Review the [Data Model](./data-model.md) for database schema
- Check the [Research](./research.md) for technical decisions
- See the [Implementation Plan](./plan.md) for architecture details

---

## Support

For issues or questions, please refer to the project documentation or contact the development team.