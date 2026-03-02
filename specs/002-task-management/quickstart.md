# Quickstart: Task Management

**Feature**: 002-task-management
**Date**: 2026-03-02

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip (Python package manager)
- Completed 001-user-auth feature (authentication system)

## Installation

### 1. Clone and Setup

```bash
cd /path/to/project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root (or update existing):

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trello

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET=your-secret-key-here

# JWT Expiration (in seconds, 24 hours = 86400)
JWT_EXPIRATION_SECONDS=86400

# Bcrypt Work Factor (recommended: 12)
BCRYPT_ROUNDS=12

# Application
APP_NAME=Trello
APP_ENV=development
DEBUG=True
```

### 4. Database Setup

```bash
# Create database (if not exists)
createdb trello

# Run all migrations (including auth and tasks)
alembic upgrade head
```

## Running the Application

### Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Register a New User (if not already registered)

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }' \
  -c cookies.txt
```

### Create a Task

```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "title": "Complete project documentation",
    "description": "Write comprehensive documentation for the new feature including API reference and user guide.",
    "due_date": "2026-03-15",
    "status": "к выполнению"
  }'
```

**Response**:
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

### Get All Tasks

```bash
curl -X GET http://localhost:8000/api/v1/tasks \
  -b cookies.txt
```

**Response**:
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
    }
  ]
}
```

### Get a Specific Task

```bash
curl -X GET http://localhost:8000/api/v1/tasks/1 \
  -b cookies.txt
```

### Update a Task

```bash
curl -X PUT http://localhost:8000/api/v1/tasks/1 \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "status": "в работу"
  }'
```

### Delete a Task

```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/1 \
  -b cookies.txt
```

### Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -b cookies.txt
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Task-Specific Tests

```bash
# Unit tests
pytest tests/unit/test_task_service.py
pytest tests/unit/test_task_validators.py

# Integration tests
pytest tests/integration/test_tasks_api.py

# Contract tests
pytest tests/contract/test_tasks_api_contract.py
```

## Project Structure

```
src/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings
├── models/
│   ├── user.py            # User SQLAlchemy model (existing)
│   ├── session.py         # Session SQLAlchemy model (existing)
│   ├── failed_login.py    # FailedLoginAttempt SQLAlchemy model (existing)
│   └── task.py            # Task SQLAlchemy model (NEW)
├── schemas/
│   ├── user.py            # Pydantic schemas for User (existing)
│   ├── auth.py            # Pydantic schemas for Auth (existing)
│   └── task.py            # Pydantic schemas for Task (NEW)
├── services/
│   ├── auth_service.py    # Authentication business logic (existing)
│   ├── password_service.py # Password hashing/validation (existing)
│   ├── rate_limit_service.py # Rate limiting logic (existing)
│   ├── session_service.py # Session management (existing)
│   └── task_service.py    # Task business logic (NEW)
├── repositories/
│   ├── user_repository.py # User data access (existing)
│   ├── session_repository.py # Session data access (existing)
│   ├── failed_login_repository.py # Failed login data access (existing)
│   └── task_repository.py # Task data access (NEW)
├── api/
│   └── v1/
│       ├── auth.py        # Auth API endpoints (existing)
│       └── tasks.py       # Task API endpoints (NEW)
└── utils/
    ├── security.py        # JWT token utilities (existing)
    ├── validators.py      # Custom validators (existing)
    └── task_validators.py # Task-specific validators (NEW)

tests/
├── unit/
│   ├── test_password_service.py (existing)
│   ├── test_auth_service.py (existing)
│   ├── test_rate_limit_service.py (existing)
│   ├── test_validators.py (existing)
│   ├── test_task_service.py (NEW)
│   └── test_task_validators.py (NEW)
├── integration/
│   ├── test_auth_api.py (existing)
│   ├── test_registration.py (existing)
│   ├── test_authentication.py (existing)
│   ├── test_logout.py (existing)
│   ├── test_rate_limiting.py (existing)
│   └── test_tasks_api.py (NEW)
└── contract/
    ├── test_auth_api_contract.py (existing)
    └── test_tasks_api_contract.py (NEW)

alembic/
├── versions/              # Database migration files
│   ├── 001_initial.py    # Initial schema migration (existing)
│   ├── 002_cleanup_jobs.py (existing)
│   └── 003_add_tasks.py  # Tasks table migration (NEW)
└── env.py                 # Alembic configuration
```

## Task Status Values

Valid task status values:
- `к выполнению` - To do
- `в работу` - In progress
- `возникла проблема` - Has issue
- `сделано` - Done
- `отмена` - Cancelled

## Development Workflow

### Adding New Task Fields

1. Update `src/models/task.py` - Add new column to Task model
2. Update `src/schemas/task.py` - Add field to Pydantic schemas
3. Create migration: `alembic revision --autogenerate -m "add new field"`
4. Run migration: `alembic upgrade head`
5. Update tests

### Adding New Task Endpoints

1. Update `src/api/v1/tasks.py` - Add new endpoint
2. Update `src/services/task_service.py` - Add business logic if needed
3. Update `src/repositories/task_repository.py` - Add data access if needed
4. Update `specs/002-task-management/contracts/api.md` - Document new endpoint
5. Add tests in `tests/integration/test_tasks_api.py`

## Troubleshooting

### Migration Issues

If migration fails:
```bash
# Check current version
alembic current

# Check migration history
alembic history

# Rollback to specific version
alembic downgrade <revision_id>
```

### Database Connection Issues

Check `.env` file has correct `DATABASE_URL`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/trello
```

### Authentication Issues

Ensure JWT_SECRET is set in `.env` and matches between server restarts.

## Next Steps

- Run `/speckit.tasks` to generate implementation task breakdown
- Review [`plan.md`](plan.md) for detailed implementation plan
- Review [`data-model.md`](data-model.md) for database schema
- Review [`contracts/api.md`](contracts/api.md) for API contract