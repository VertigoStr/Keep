# src Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-03-02

## Active Technologies
- Python 3.11 + FastAPI, SQLAlchemy, Pydantic (002-task-management)
- PostgreSQL (002-task-management)
- pytest, pytest-asyncio, httpx (002-task-management)
- Alembic for database migrations (002-task-management)
- Python 3.11 + FastAPI, SQLAlchemy, Pydantic, Alembic (003-board-management)

- (001-user-auth)

## Project Structure

```text
src/
├── models/          # SQLAlchemy ORM models
├── schemas/         # Pydantic schemas for validation
├── services/        # Business logic layer
├── repositories/    # Data access layer
├── api/             # API endpoints
│   └── v1/          # API version 1
└── utils/           # Utility functions

tests/
├── unit/            # Unit tests
├── integration/     # Integration tests
└── contract/        # Contract tests
```

## Commands

# Build
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database
alembic upgrade head
alembic revision --autogenerate -m "description"

# Run
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Test
pytest
pytest --cov=src --cov-report=html
pytest tests/unit/test_task_service.py

## Code Style

: Follow standard conventions
- PEP8 compliance
- snake_case naming
- Max 120 char lines
- SOLID, DRY, KISS principles
- 80% test coverage target

## Recent Changes
- 003-board-management: Added Python 3.11 + FastAPI, SQLAlchemy, Pydantic, Alembic
- 002-task-management: Added Python 3.11 + FastAPI, SQLAlchemy, Pydantic, pytest, Alembic
- 002-task-management: Task management with CRUD operations, status management, user ownership


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
