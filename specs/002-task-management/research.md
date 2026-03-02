# Research: Task Management Feature

**Feature**: 002-task-management
**Date**: 2026-03-02
**Status**: Complete

## Overview

This document consolidates research findings for the task management feature, covering technology choices, best practices, and design decisions.

## Research Topics

### 1. Task Status Representation

**Question**: How to represent predefined task statuses in Python/FastAPI?

**Decision**: Use Python `Enum` with string values

**Rationale**:
- Type-safe: Prevents invalid status values at compile time
- Self-documenting: Enum members clearly show available options
- Pydantic integration: Works seamlessly with Pydantic models for validation
- Database mapping: SQLAlchemy can map Enum to VARCHAR or ENUM column types
- Easy to extend: Adding new statuses is straightforward

**Alternatives Considered**:
- String literals: No type safety, prone to typos
- Database ENUM: Less flexible, requires migration for changes
- Integer codes: Less readable, requires mapping

**Implementation**:
```python
from enum import Enum

class TaskStatus(str, Enum):
    TODO = "к выполнению"
    IN_PROGRESS = "в работу"
    HAS_ISSUE = "возникла проблема"
    DONE = "сделано"
    CANCELLED = "отмена"
```

### 2. Description Field Validation

**Question**: How to validate description length (0-5000 characters)?

**Decision**: Use Pydantic field validator with `max_length` constraint

**Rationale**:
- Built-in Pydantic support: `max_length` parameter on `Field()`
- Automatic error messages: Pydantic provides clear validation errors
- Database-level validation: SQLAlchemy `String(5000)` enforces at DB level
- Performance: Simple length check is fast

**Alternatives Considered**:
- Custom validator function: More complex, unnecessary for simple length check
- Database-only validation: No feedback before DB write
- JavaScript validation: Client-side only, not sufficient

**Implementation**:
```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1)
    description: str = Field("", max_length=5000)
    # ...
```

### 3. Due Date Format and Storage

**Question**: How to handle due date in YYYY-MM-DD format?

**Decision**: Use Python `date` type in Pydantic, `DATE` column in PostgreSQL

**Rationale**:
- Type safety: `date` type prevents invalid dates
- ISO 8601 format: Pydantic serializes `date` to YYYY-MM-DD by default
- Database support: PostgreSQL `DATE` type is efficient for date-only values
- Timezone handling: No timezone issues with date-only values
- Validation: Pydantic validates date format automatically

**Alternatives Considered**:
- String with regex: No type safety, manual validation
- DateTime with time: Unnecessary complexity, timezone issues
- Unix timestamp: Not human-readable, requires conversion

**Implementation**:
```python
from datetime import date

class TaskCreate(BaseModel):
    due_date: date
    # ...
```

### 4. User Ownership and Access Control

**Question**: How to ensure users can only access their own tasks?

**Decision**: Foreign key relationship with ownership checks in service layer

**Rationale**:
- Database integrity: Foreign key ensures referential integrity
- Cascade delete: Tasks deleted when user is deleted
- Service layer validation: Business logic checks ownership before operations
- Repository filtering: Queries automatically filter by user_id
- Consistent with existing auth feature: Reuses User model

**Alternatives Considered**:
- Row-level security: More complex, PostgreSQL-specific
- Shared tasks with permissions: Over-engineering for current requirements
- No ownership check: Security vulnerability

**Implementation**:
```python
# Model
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    # ...

# Repository
def get_user_tasks(self, user_id: int) -> List[Task]:
    return self.session.query(Task).filter(Task.user_id == user_id).all()
```

### 5. Status Transition Rules

**Question**: Should status transitions be restricted?

**Decision**: No restrictions - any status can be set to any other status

**Rationale**:
- Spec requirement: "Статус задачи может быть изменён в любом направлении"
- Flexibility: Users can correct mistakes or change workflow
- Simplicity: No complex state machine logic
- Future-proof: Easy to add restrictions later if needed

**Alternatives Considered**:
- State machine with allowed transitions: Over-engineering for current needs
- Prevent certain transitions (e.g., DONE → TODO): Too restrictive
- Audit trail only: Adds complexity without functional benefit

**Implementation**:
```python
# No transition validation - direct assignment allowed
task.status = new_status
```

### 6. Task Listing and Sorting

**Question**: How should tasks be listed and sorted?

**Decision**: Simple SELECT without sorting (as stored in DB)

**Rationale**:
- Spec requirement: "Без сортировки (как хранятся в БД)"
- Performance: No ORDER BY clause is faster
- Simplicity: Minimal query complexity
- Consistent with spec: Explicitly requested behavior

**Alternatives Considered**:
- Sort by due date: Not requested
- Sort by status: Not requested
- Sort by creation date: Not requested
- Custom sorting: Over-engineering

**Implementation**:
```python
def get_user_tasks(self, user_id: int) -> List[Task]:
    return self.session.query(Task).filter(Task.user_id == user_id).all()
```

### 7. Database Migration Strategy

**Question**: How to add tasks table to existing database?

**Decision**: Use Alembic migration (003_add_tasks.py)

**Rationale**:
- Existing infrastructure: Project already uses Alembic
- Version control: Migrations tracked in git
- Rollback support: Can undo changes if needed
- Consistent with existing pattern: Follows 001_initial.py and 002_cleanup_jobs.py

**Alternatives Considered**:
- Manual SQL: No version control, error-prone
- Drop and recreate: Loses existing data
- No migration: Manual setup required

**Implementation**:
```python
# alembic/versions/003_add_tasks.py
def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE')),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.String(5000), nullable=False),
        sa.Column('due_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
```

### 8. API Endpoint Design

**Question**: What REST endpoints are needed for task management?

**Decision**: CRUD endpoints following REST conventions

**Rationale**:
- RESTful design: Standard HTTP methods (GET, POST, PUT, DELETE)
- Consistent with auth endpoints: Follows existing pattern
- Clear semantics: Easy to understand and use
- Swagger documentation: Auto-generated from FastAPI

**Endpoints**:
- `POST /api/v1/tasks` - Create task
- `GET /api/v1/tasks` - List user's tasks
- `GET /api/v1/tasks/{task_id}` - Get specific task
- `PUT /api/v1/tasks/{task_id}` - Update task (including status)
- `DELETE /api/v1/tasks/{task_id}` - Delete task

**Alternatives Considered**:
- GraphQL: Over-engineering for simple CRUD
- RPC-style: Less standard, harder to document
- Separate status endpoint: Unnecessary complexity

### 9. Authentication Integration

**Question**: How to protect task endpoints with authentication?

**Decision**: Reuse existing JWT authentication middleware

**Rationale**:
- Existing infrastructure: Auth feature already implements JWT
- Consistent security: Same authentication mechanism across all endpoints
- User context: JWT provides user_id for ownership checks
- Minimal code: Reuse existing `get_current_user` dependency

**Implementation**:
```python
from src.utils.security import get_current_user

@router.post("/tasks", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user)
):
    # current_user.id used for ownership
    ...
```

### 10. Testing Strategy

**Question**: How to test task management functionality?

**Decision**: Three-tier testing (unit, integration, contract)

**Rationale**:
- Unit tests: Test service layer logic in isolation
- Integration tests: Test API endpoints with database
- Contract tests: Verify API contract compliance
- Consistent with existing pattern: Auth feature uses same approach

**Test Coverage**:
- Unit: `test_task_service.py`, `test_task_validators.py`
- Integration: `test_tasks_api.py`
- Contract: `test_tasks_api_contract.py`

**Alternatives Considered**:
- Only integration tests: Slower, harder to pinpoint issues
- Only unit tests: Doesn't test full request/response cycle
- E2E tests: Over-engineering for backend-only feature

## Summary

All research topics have been resolved with clear decisions aligned with:
- Project constitution (Python 3.11, FastAPI, PEP8)
- Existing architecture (layered design, repository pattern)
- Feature specification requirements
- Best practices for FastAPI/PostgreSQL applications

No blockers identified. Proceeding to Phase 1 design.