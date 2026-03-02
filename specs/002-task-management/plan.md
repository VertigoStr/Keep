# Implementation Plan: Task Management

**Branch**: `002-task-management` | **Date**: 2026-03-02 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-task-management/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement task management system allowing authenticated users to create, view, and update tasks. Tasks include title (required), description (0-5000 characters), due date (YYYY-MM-DD format), and status from predefined list: "к выполнению", "в работу", "возникла проблема", "сделано", "отмена". Users can only access their own tasks. Technical approach extends existing FastAPI/PostgreSQL architecture with new Task model, repository, service layer, and API endpoints.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLAlchemy, Pydantic
**Storage**: PostgreSQL
**Testing**: pytest, pytest-asyncio, httpx
**Target Platform**: Linux server
**Project Type**: web-service
**Performance Goals**: 1000 concurrent requests, <200ms p95 response time
**Constraints**: 99.99% uptime, 80% test coverage, PEP8 compliance
**Scale/Scope**: Initial deployment for 1000+ concurrent users, support for 10,000+ tasks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Phase 0 Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Language: Python 3.11 | ✅ PASS | Specified in constitution |
| Framework: FastAPI | ✅ PASS | Specified in constitution |
| PEP8 compliance | ✅ PASS | Will be enforced via linters |
| SOLID/DRY/KISS | ✅ PASS | Layered architecture planned |
| snake_case naming | ✅ PASS | Will be enforced |
| Max 120 char lines | ✅ PASS | Will be enforced |
| Documentation | ✅ PASS | All methods/classes documented |
| Unit tests required | ✅ PASS | 80% coverage target |
| Security: env vars | ✅ PASS | Secrets in environment |
| One commit = one task | ✅ PASS | Will be enforced in PR review |

**Result**: ✅ All gates passed. Proceeding to Phase 0.

### Post-Phase 1 Check

| Principle | Status | Notes |
|-----------|--------|-------|
| Language: Python 3.11 | ✅ PASS | Confirmed in research |
| Framework: FastAPI | ✅ PASS | Confirmed in research |
| PEP8 compliance | ✅ PASS | Project structure follows PEP8 |
| SOLID/DRY/KISS | ✅ PASS | Service layer separation implemented |
| snake_case naming | ✅ PASS | All entities use snake_case |
| Max 120 char lines | ✅ PASS | Code style enforced |
| Documentation | ✅ PASS | API docs via Swagger, code docs |
| Unit tests required | ✅ PASS | Test structure defined |
| Security: env vars | ✅ PASS | DATABASE_URL in env |
| One commit = one task | ✅ PASS | Task breakdown supports this |

**Result**: ✅ All gates passed. Design is compliant.

## Project Structure

### Documentation (this feature)

```text
specs/002-task-management/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
│   └── api.md          # API contract specification
├── checklists/
│   └── requirements.md # Specification quality checklist
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings (pydantic-settings)
├── models/
│   ├── __init__.py
│   ├── user.py            # User SQLAlchemy model (existing)
│   ├── session.py         # Session SQLAlchemy model (existing)
│   ├── failed_login.py    # FailedLoginAttempt SQLAlchemy model (existing)
│   └── task.py            # Task SQLAlchemy model (NEW)
├── schemas/
│   ├── __init__.py
│   ├── user.py            # Pydantic schemas for User (existing)
│   ├── auth.py            # Pydantic schemas for Auth (existing)
│   └── task.py            # Pydantic schemas for Task (NEW)
├── services/
│   ├── __init__.py
│   ├── auth_service.py    # Authentication business logic (existing)
│   ├── password_service.py # Password hashing/validation (existing)
│   ├── rate_limit_service.py # Rate limiting logic (existing)
│   ├── session_service.py # Session management (existing)
│   └── task_service.py    # Task business logic (NEW)
├── repositories/
│   ├── __init__.py
│   ├── user_repository.py # User data access (existing)
│   ├── session_repository.py # Session data access (existing)
│   ├── failed_login_repository.py # Failed login data access (existing)
│   └── task_repository.py # Task data access (NEW)
├── api/
│   ├── __init__.py
│   └── v1/
│       ├── __init__.py
│       ├── auth.py        # Auth API endpoints (existing)
│       └── tasks.py       # Task API endpoints (NEW)
└── utils/
    ├── __init__.py
    ├── security.py        # JWT token utilities (existing)
    ├── validators.py      # Custom validators (existing)
    └── task_validators.py # Task-specific validators (NEW)

tests/
├── __init__.py
├── conftest.py            # Pytest fixtures
├── unit/
│   ├── __init__.py
│   ├── test_password_service.py (existing)
│   ├── test_auth_service.py (existing)
│   ├── test_rate_limit_service.py (existing)
│   ├── test_validators.py (existing)
│   ├── test_task_service.py (NEW)
│   └── test_task_validators.py (NEW)
├── integration/
│   ├── __init__.py
│   ├── test_auth_api.py (existing)
│   ├── test_registration.py (existing)
│   ├── test_authentication.py (existing)
│   ├── test_logout.py (existing)
│   ├── test_rate_limiting.py (existing)
│   └── test_tasks_api.py (NEW)
└── contract/
    ├── __init__.py
    ├── test_auth_api_contract.py (existing)
    └── test_tasks_api_contract.py (NEW)

alembic/
├── versions/              # Database migration files
│   ├── 001_initial.py    # Initial schema migration (existing)
│   ├── 002_cleanup_jobs.py (existing)
│   └── 003_add_tasks.py  # Tasks table migration (NEW)
└── env.py                 # Alembic configuration

.env.example               # Environment variables template
requirements.txt           # Python dependencies
pytest.ini                 # Pytest configuration
```

**Structure Decision**: Single project structure (Option 1) selected as this is a web service extending the existing user-auth feature. The layered architecture (API → Service → Repository → Database) follows SOLID principles and enables independent testing of each layer. New task management components integrate seamlessly with existing authentication infrastructure.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. All constitution principles are satisfied by the proposed design.

## Phase 0: Research

**Status**: ✅ Complete

**Output**: [`research.md`](research.md)

**Key Decisions**:
- Task status enum: Python Enum with string values for predefined statuses
- Description validation: Pydantic field validator with max_length=5000
- Due date format: date type in Pydantic, DATE column in PostgreSQL
- User ownership: Foreign key to User model with CASCADE delete
- Status transitions: No restrictions (any status can be set to any other status)
- Task listing: Simple SELECT without sorting (as stored in DB)

## Phase 1: Design

**Status**: ✅ Complete

**Outputs**:
- [`data-model.md`](data-model.md) - Database schema and entities
- [`contracts/api.md`](contracts/api.md) - API contract specification
- [`quickstart.md`](quickstart.md) - Developer quickstart guide

**Key Design Decisions**:
- Task model with user_id foreign key for ownership
- Pydantic schemas for request/response validation
- Service layer for business logic (status validation, ownership checks)
- Repository pattern for data access
- API endpoints protected by JWT authentication middleware
- Status validation using Python Enum

## Next Steps

Run `/speckit.tasks` to generate the implementation task breakdown.