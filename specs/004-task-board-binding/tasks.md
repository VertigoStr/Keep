---

description: "Task list for Task to Board Binding feature implementation"

---

# Tasks: Task to Board Binding

**Input**: Design documents from `/specs/004-task-board-binding/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md

**Tests**: Included as per constitution requirements (80% coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create database migration for board_id in tasks table in alembic/versions/
- [ ] T002 [P] Apply database migration using alembic upgrade head
- [ ] T003 [P] Verify database schema changes in PostgreSQL

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create Task model with board_id field in src/models/task.py
- [ ] T005 [P] Create Board model with is_default field in src/models/board.py
- [ ] T006 [P] Update Task schema with board_id in src/schemas/task.py
- [ ] T007 [P] Update Board schema with is_default in src/schemas/board.py
- [ ] T008 Create TaskRepository with board-related methods in src/repositories/task_repository.py
- [ ] T009 [P] Create BoardRepository with default board methods in src/repositories/board_repository.py
- [ ] T010 Create TaskService with board binding logic in src/services/task_service.py
- [ ] T011 [P] Create BoardService with default board management in src/services/board_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Автоматическая привязка задачи к доске при создании (Priority: P1) 🎯 MVP

**Goal**: Пользователь создает новую задачу, и система автоматически привязывает её к его доске по умолчанию

**Independent Test**: Создать новую задачу без указания доски и проверить, что она автоматически привязана к доске пользователя по умолчанию

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T012 [P] [US1] Unit test for TaskRepository.get_default_board in tests/unit/test_task_repository.py
- [ ] T013 [P] [US1] Unit test for TaskService.create_task with auto-binding in tests/unit/test_task_service.py
- [ ] T014 [P] [US1] Integration test for auto board binding in tests/integration/test_task_board_binding.py
- [ ] T015 [P] [US1] Contract test for POST /tasks endpoint in tests/contract/test_task_board_api.py

### Implementation for User Story 1

- [ ] T016 [US1] Implement get_default_board method in TaskRepository in src/repositories/task_repository.py
- [ ] T017 [US1] Implement create_default_board method in BoardService in src/services/board_service.py
- [ ] T018 [US1] Implement auto board binding logic in TaskService.create_task in src/services/task_service.py
- [ ] T019 [US1] Update POST /tasks endpoint to support auto-binding in src/api/v1/tasks.py
- [ ] T020 [US1] Add validation for board ownership in TaskService in src/services/task_service.py
- [ ] T021 [US1] Add error handling for missing default board in TaskService in src/services/task_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Ручная привязка задачи к конкретной доске (Priority: P2)

**Goal**: Пользователь может явно указать, к какой доске привязать задачу при её создании или редактировании

**Independent Test**: Создать задачу с указанием конкретной доски и проверить, что задача привязана к указанной доске

### Tests for User Story 2

- [ ] T022 [P] [US2] Unit test for TaskService.create_task with explicit board in tests/unit/test_task_service.py
- [ ] T023 [P] [US2] Unit test for TaskService.update_task board change in tests/unit/test_task_service.py
- [ ] T024 [P] [US2] Integration test for explicit board binding in tests/integration/test_task_board_binding.py
- [ ] T025 [P] [US2] Contract test for PUT /tasks/{task_id} endpoint in tests/contract/test_task_board_api.py

### Implementation for User Story 2

- [ ] T026 [US2] Implement explicit board_id parameter in TaskService.create_task in src/services/task_service.py
- [ ] T027 [US2] Implement board_id update in TaskService.update_task in src/services/task_service.py
- [ ] T028 [US2] Add board ownership validation in TaskService in src/services/task_service.py
- [ ] T029 [US2] Update PUT /tasks/{task_id} endpoint to support board change in src/api/v1/tasks.py
- [ ] T030 [US2] Add error handling for non-existent board in TaskService in src/services/task_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Просмотр задач в контексте доски (Priority: P3)

**Goal**: Пользователь может просматривать все задачи, привязанные к конкретной доске

**Independent Test**: Открыть доску и проверить, что отображаются только задачи, привязанные к этой доске

### Tests for User Story 3

- [ ] T031 [P] [US3] Unit test for TaskRepository.get_board_tasks in tests/unit/test_task_repository.py
- [ ] T032 [P] [US3] Integration test for board tasks retrieval in tests/integration/test_board_tasks.py
- [ ] T033 [P] [US3] Contract test for GET /boards/{board_id}/tasks endpoint in tests/contract/test_task_board_api.py

### Implementation for User Story 3

- [ ] T034 [US3] Implement get_board_tasks method in TaskRepository in src/repositories/task_repository.py
- [ ] T035 [US3] Implement get_board_tasks method in TaskService in src/services/task_service.py
- [ ] T036 [US3] Add board ownership check in TaskService.get_board_tasks in src/services/task_service.py
- [ ] T037 [US3] Implement GET /boards/{board_id}/tasks endpoint in src/api/v1/boards.py
- [ ] T038 [US3] Add pagination support for board tasks in src/api/v1/boards.py
- [ ] T039 [US3] Add status filtering for board tasks in src/api/v1/boards.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Additional Board Management Features

**Goal**: Дополнительные функции для управления досками (создание, установка по умолчанию, удаление)

**Independent Test**: Создать доску, пометить её как по умолчанию, затем удалить и проверить каскадное удаление задач

### Tests for Board Management

- [ ] T040 [P] [Board] Unit test for BoardRepository.set_default_board in tests/unit/test_board_repository.py
- [ ] T041 [P] [Board] Unit test for BoardService.delete_board with cascade in tests/unit/test_board_service.py
- [ ] T042 [P] [Board] Integration test for board lifecycle in tests/integration/test_board_tasks.py
- [ ] T043 [P] [Board] Contract test for board endpoints in tests/contract/test_task_board_api.py

### Implementation for Board Management

- [ ] T044 [Board] Implement set_default_board method in BoardRepository in src/repositories/board_repository.py
- [ ] T045 [Board] Implement set_default_board method in BoardService in src/services/board_service.py
- [ ] T046 [Board] Implement delete_board with cascade in BoardService in src/services/board_service.py
- [ ] T047 [Board] Implement POST /boards endpoint with is_default in src/api/v1/boards.py
- [ ] T048 [Board] Implement PUT /boards/{board_id}/set-default endpoint in src/api/v1/boards.py
- [ ] T049 [Board] Implement GET /boards/default endpoint in src/api/v1/boards.py
- [ ] T050 [Board] Implement DELETE /boards/{board_id} endpoint in src/api/v1/boards.py
- [ ] T051 [Board] Add auto-assign default board on delete in BoardService in src/services/board_service.py

**Checkpoint**: All board management features should be functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T052 [P] Add logging for all task-board operations in src/utils/logging.py
- [ ] T053 [P] Add performance optimization with eager loading in src/repositories/task_repository.py
- [ ] T054 [P] Add database indexes for board_id in alembic/versions/
- [ ] T055 Update API documentation in src/api/v1/tasks.py and src/api/v1/boards.py
- [ ] T056 Run test coverage and ensure 80% target is met
- [ ] T057 Validate quickstart.md examples work correctly
- [ ] T058 Code cleanup and refactoring for SOLID principles
- [ ] T059 Add input validation and sanitization in src/schemas/task.py and src/schemas/board.py

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → Board)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 models and services
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 and US2 models
- **Board Management**: Can start after Foundational (Phase 2) - Independent of user stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Terminal 1: Write tests (parallel)
- T012: Unit test for TaskRepository.get_default_board
- T013: Unit test for TaskService.create_task with auto-binding
- T014: Integration test for auto board binding
- T015: Contract test for POST /tasks endpoint

# Terminal 2: Implement (after tests fail)
- T016: Implement get_default_board method
- T017: Implement create_default_board method
- T018: Implement auto board binding logic
- T019: Update POST /tasks endpoint
- T020: Add validation for board ownership
- T021: Add error handling for missing default board
```

---

## Parallel Example: User Story 2

```bash
# Terminal 1: Write tests (parallel)
- T022: Unit test for TaskService.create_task with explicit board
- T023: Unit test for TaskService.update_task board change
- T024: Integration test for explicit board binding
- T025: Contract test for PUT /tasks/{task_id} endpoint

# Terminal 2: Implement (after tests fail)
- T026: Implement explicit board_id parameter
- T027: Implement board_id update
- T028: Add board ownership validation
- T029: Update PUT /tasks/{task_id} endpoint
- T030: Add error handling for non-existent board
```

---

## Parallel Example: User Story 3

```bash
# Terminal 1: Write tests (parallel)
- T031: Unit test for TaskRepository.get_board_tasks
- T032: Integration test for board tasks retrieval
- T033: Contract test for GET /boards/{board_id}/tasks endpoint

# Terminal 2: Implement (after tests fail)
- T034: Implement get_board_tasks method in repository
- T035: Implement get_board_tasks method in service
- T036: Add board ownership check
- T037: Implement GET /boards/{board_id}/tasks endpoint
- T038: Add pagination support
- T039: Add status filtering
```

---

## Implementation Strategy

### MVP Scope (Minimum Viable Product)

**Recommended MVP**: Phase 1 + Phase 2 + Phase 3 (User Story 1)

This delivers:
- Automatic task binding to default board
- Basic task creation with board association
- Foundation for future stories

**MVP Test Criteria**:
1. User can create a task without specifying board
2. Task is automatically bound to user's default board
3. If no default board exists, one is created automatically
4. All tests for US1 pass

### Incremental Delivery

**Sprint 1**: MVP (US1) - Core auto-binding functionality
**Sprint 2**: US2 - Explicit board binding and task reassignment
**Sprint 3**: US3 - Board task viewing and filtering
**Sprint 4**: Board Management - Full board lifecycle
**Sprint 5**: Polish - Performance, documentation, 80% coverage

### Risk Mitigation

- **Database Migration**: Test migration on staging before production
- **Cascade Delete**: Verify cascade behavior with test data
- **Performance**: Add indexes early (T054) for large datasets
- **Security**: Validate board ownership on all operations

---

## Task Summary

- **Total Tasks**: 59
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 8 tasks
- **User Story 1 (P1)**: 10 tasks (4 tests + 6 implementation)
- **User Story 2 (P2)**: 9 tasks (4 tests + 5 implementation)
- **User Story 3 (P3)**: 9 tasks (3 tests + 6 implementation)
- **Board Management**: 12 tasks (4 tests + 8 implementation)
- **Polish Phase**: 8 tasks

**Parallel Opportunities**: 28 tasks marked [P] for parallel execution

**Independent Test Criteria**:
- US1: Create task without board → auto-bound to default board
- US2: Create task with board → bound to specified board
- US3: Get board tasks → only tasks on that board returned
- Board: Create/set default/delete → full lifecycle works

**MVP Scope**: 21 tasks (Setup + Foundational + US1)