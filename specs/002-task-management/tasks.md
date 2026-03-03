---

description: "Task list for Task Management feature implementation"
---

# Tasks: Task Management

**Input**: Design documents from `/specs/002-task-management/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as the project targets 80% test coverage per constitution requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below follow the project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create database migration for tasks table in alembic/versions/003_add_tasks.py
- [X] T002 [P] Create TaskStatus enum in src/models/task.py
- [X] T003 [P] Create Task SQLAlchemy model in src/models/task.py
- [X] T004 [P] Create Task Pydantic schemas in src/schemas/task.py
- [X] T005 [P] Create task validators in src/utils/task_validators.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Create TaskRepository in src/repositories/task_repository.py
- [X] T007 [P] Create TaskService in src/services/task_service.py
- [X] T008 [P] Create task API router in src/api/v1/tasks.py
- [X] T009 Register task router in src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Создание новой задачи (Priority: P1) 🎯 MVP

**Goal**: Пользователь может создать новую задачу, указав название, описание, срок исполнения и начальный статус

**Independent Test**: Создать одну задачу через API и проверить её сохранение в системе. Пользователь может зафиксировать задачу в системе.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T010 [P] [US1] Unit test for TaskRepository.create_task in tests/unit/test_task_repository.py
- [X] T011 [P] [US1] Unit test for TaskService.create_task in tests/unit/test_task_service.py
- [X] T012 [P] [US1] Integration test for POST /tasks endpoint in tests/integration/test_tasks_api.py
- [X] T013 [P] [US1] Contract test for POST /tasks in tests/contract/test_tasks_api_contract.py

### Implementation for User Story 1

- [X] T014 [US1] Implement TaskRepository.create_task method in src/repositories/task_repository.py
- [X] T015 [US1] Implement TaskService.create_task method in src/services/task_service.py (depends on T014)
- [X] T016 [US1] Implement POST /tasks endpoint in src/api/v1/tasks.py (depends on T015)
- [X] T017 [US1] Add validation for title (required, 1-255 chars) in src/schemas/task.py
- [X] T018 [US1] Add validation for description (0-5000 chars) in src/schemas/task.py
- [X] T019 [US1] Add validation for due_date (YYYY-MM-DD format) in src/schemas/task.py
- [X] T020 [US1] Add validation for status (predefined values) in src/schemas/task.py
- [X] T021 [US1] Add error handling for validation errors in src/api/v1/tasks.py
- [X] T022 [US1] Add logging for task creation in src/services/task_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Просмотр списка задач (Priority: P2)

**Goal**: Пользователь может просмотреть список всех созданных задач с их основными параметрами

**Independent Test**: Создать несколько задач и проверить их отображение в списке. Пользователь видит все свои задачи в одном месте.

### Tests for User Story 2

- [X] T023 [P] [US2] Unit test for TaskRepository.get_user_tasks in tests/unit/test_task_repository.py
- [X] T024 [P] [US2] Unit test for TaskService.get_user_tasks in tests/unit/test_task_service.py
- [X] T025 [P] [US2] Integration test for GET /tasks endpoint in tests/integration/test_tasks_api.py
- [X] T026 [P] [US2] Contract test for GET /tasks in tests/contract/test_tasks_api_contract.py

### Implementation for User Story 2

- [X] T027 [US2] Implement TaskRepository.get_user_tasks method in src/repositories/task_repository.py
- [X] T028 [US2] Implement TaskService.get_user_tasks method in src/services/task_service.py (depends on T027)
- [X] T029 [US2] Implement GET /tasks endpoint in src/api/v1/tasks.py (depends on T028)
- [X] T030 [US2] Add ownership check to ensure user only sees their own tasks in src/services/task_service.py
- [X] T031 [US2] Add error handling for empty task list in src/api/v1/tasks.py
- [X] T032 [US2] Add logging for task list retrieval in src/services/task_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Изменение статуса задачи (Priority: P3)

**Goal**: Пользователь может изменить статус существующей задачи на один из предопределённых статусов

**Independent Test**: Создать задачу и последовательно изменить её статус. Пользователь может отражать текущее состояние задачи.

### Tests for User Story 3

- [X] T033 [P] [US3] Unit test for TaskRepository.get_task_by_id in tests/unit/test_task_repository.py
- [X] T034 [P] [US3] Unit test for TaskRepository.update_task in tests/unit/test_task_repository.py
- [X] T035 [P] [US3] Unit test for TaskRepository.is_task_owner in tests/unit/test_task_repository.py
- [X] T036 [P] [US3] Unit test for TaskService.update_task_status in tests/unit/test_task_service.py
- [X] T037 [P] [US3] Integration test for GET /tasks/{task_id} endpoint in tests/integration/test_tasks_api.py
- [X] T038 [P] [US3] Integration test for PUT /tasks/{task_id} endpoint in tests/integration/test_tasks_api.py
- [X] T039 [P] [US3] Contract test for GET /tasks/{task_id} in tests/contract/test_tasks_api_contract.py
- [X] T040 [P] [US3] Contract test for PUT /tasks/{task_id} in tests/contract/test_tasks_api_contract.py

### Implementation for User Story 3

- [X] T041 [US3] Implement TaskRepository.get_task_by_id method in src/repositories/task_repository.py
- [X] T042 [US3] Implement TaskRepository.update_task method in src/repositories/task_repository.py
- [X] T043 [US3] Implement TaskRepository.is_task_owner method in src/repositories/task_repository.py
- [X] T044 [US3] Implement TaskService.update_task_status method in src/services/task_service.py (depends on T041, T042, T043)
- [X] T045 [US3] Implement GET /tasks/{task_id} endpoint in src/api/v1/tasks.py (depends on T041, T044)
- [X] T046 [US3] Implement PUT /tasks/{task_id} endpoint in src/api/v1/tasks.py (depends on T042, T044)
- [X] T047 [US3] Add ownership check for task access in src/services/task_service.py
- [X] T048 [US3] Add validation for status update (any status allowed) in src/schemas/task.py
- [X] T049 [US3] Add error handling for task not found in src/api/v1/tasks.py
- [X] T050 [US3] Add error handling for forbidden access in src/api/v1/tasks.py
- [X] T051 [US3] Add logging for task status updates in src/services/task_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Additional CRUD Operations (Supporting All User Stories)

**Goal**: Complete CRUD operations for tasks (delete operation)

**Independent Test**: Создать задачу и удалить её. Проверить, что задача удалена из системы.

### Tests for Additional Operations

- [X] T052 [P] Unit test for TaskRepository.delete_task in tests/unit/test_task_repository.py
- [X] T053 [P] Unit test for TaskService.delete_task in tests/unit/test_task_service.py
- [X] T054 [P] Integration test for DELETE /tasks/{task_id} endpoint in tests/integration/test_tasks_api.py
- [X] T055 [P] Contract test for DELETE /tasks/{task_id} in tests/contract/test_tasks_api_contract.py

### Implementation for Additional Operations

- [X] T056 Implement TaskRepository.delete_task method in src/repositories/task_repository.py
- [X] T057 Implement TaskService.delete_task method in src/services/task_service.py (depends on T056)
- [X] T058 Implement DELETE /tasks/{task_id} endpoint in src/api/v1/tasks.py (depends on T057)
- [X] T059 Add ownership check for task deletion in src/services/task_service.py
- [X] T060 Add error handling for delete operations in src/api/v1/tasks.py
- [X] T061 Add logging for task deletion in src/services/task_service.py

**Checkpoint**: All CRUD operations complete

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T062 [P] Update README.md with task management API documentation
- [X] T063 [P] Update .env.example with any new environment variables if needed
- [X] T064 Run all tests and ensure 80% coverage target is met
- [X] T065 Run quickstart.md validation to ensure all examples work
- [X] T066 [P] Add docstrings to all new classes and methods
- [X] T067 [P] Verify PEP8 compliance with linter
- [X] T068 [P] Add type hints to all new functions
- [X] T069 Security review: verify ownership checks on all endpoints
- [X] T070 Performance review: verify database queries are optimized

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - May integrate with US1 but should be independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - May integrate with US1/US2 but should be independently testable
- **Additional CRUD (Phase 6)**: Can start after Foundational (Phase 2) - Supports all user stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Terminal 1: Write tests (parallel)
- T010: Unit test for TaskRepository.create_task
- T011: Unit test for TaskService.create_task
- T012: Integration test for POST /tasks
- T013: Contract test for POST /tasks

# Terminal 2: Implement repository (after tests fail)
- T014: Implement TaskRepository.create_task

# Terminal 3: Implement service (after T014)
- T015: Implement TaskService.create_task

# Terminal 4: Implement endpoint (after T015)
- T016: Implement POST /tasks endpoint

# Terminal 5: Add validations (parallel after T016)
- T017: Title validation
- T018: Description validation
- T019: Due date validation
- T020: Status validation

# Terminal 6: Add error handling and logging (parallel)
- T021: Error handling
- T022: Logging
```

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**MVP = User Story 1 only** - This delivers the core value of creating tasks.

**MVP Tasks**: T001-T022 (Setup + Foundational + User Story 1)

**MVP Deliverables**:
- Users can create tasks with title, description, due date, and status
- All validations in place
- Tests passing
- Ready for user feedback

### Incremental Delivery

After MVP validation, deliver remaining stories in priority order:

1. **Sprint 2**: User Story 2 (T023-T032) - Task listing
2. **Sprint 3**: User Story 3 (T033-T051) - Status updates
3. **Sprint 4**: Additional CRUD (T052-T061) - Delete operations
4. **Sprint 5**: Polish (T062-T070) - Documentation, coverage, optimization

### Risk Mitigation

- **Early testing**: Tests written first ensure requirements are clear
- **Independent stories**: Each story can be deployed independently
- **Ownership checks**: Security built in from the start
- **Validation first**: Pydantic schemas prevent invalid data at the boundary

---

## Summary

**Total Tasks**: 70

**Tasks by User Story**:
- Setup (Phase 1): 5 tasks
- Foundational (Phase 2): 4 tasks
- User Story 1 (P1): 13 tasks (4 tests + 9 implementation)
- User Story 2 (P2): 10 tasks (4 tests + 6 implementation)
- User Story 3 (P3): 19 tasks (8 tests + 11 implementation)
- Additional CRUD (Phase 6): 10 tasks (4 tests + 6 implementation)
- Polish (Phase 7): 9 tasks

**Parallel Opportunities**:
- 5 parallel tasks in Setup phase
- 2 parallel tasks in Foundational phase
- 4 parallel test tasks per user story
- User stories can be developed in parallel after Foundational phase

**Independent Test Criteria**:
- **US1**: Create task via API, verify saved in database
- **US2**: Create multiple tasks, verify list displays all
- **US3**: Create task, change status, verify update persists

**Suggested MVP**: User Story 1 (T001-T022) - 22 tasks for core task creation functionality