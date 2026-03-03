---

description: "Task list for Board Management feature implementation"
---

# Tasks: Board Management

**Input**: Design documents from `/specs/003-board-management/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: Tests are included as per project requirements (80% coverage target)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create database migration for boards table in alembic/versions/004_add_boards.py
- [x] T002 Create database migration for columns table in alembic/versions/005_add_columns.py
- [x] T003 Create database migration for adding column_id to tasks table in alembic/versions/006_add_task_column.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 [P] Create Board model in src/models/board.py
- [x] T005 [P] Create Column model in src/models/column.py
- [x] T006 Update User model to add boards relationship in src/models/user.py
- [x] T007 Update Task model to add column_id field and column relationship in src/models/task.py
- [x] T008 [P] Create BoardRepository in src/repositories/board_repository.py
- [x] T009 [P] Create ColumnRepository in src/repositories/column_repository.py
- [x] T010 [P] Create Pydantic schemas for boards in src/schemas/board.py
- [x] T011 [P] Create board validators in src/utils/board_validators.py
- [x] T012 Create BoardService in src/services/board_service.py
- [x] T013 Register board routes in src/api/v1/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Создание доски с предопределёнными колонками (Priority: P1) 🎯 MVP

**Goal**: Пользователь может создать новую доску с пятью предопределёнными колонками

**Independent Test**: Создать доску через API и проверить, что все пять колонок созданы с правильными названиями в правильном порядке

### Tests for User Story 1

- [x] T014 [P] [US1] Contract test for POST /boards in tests/contract/test_board_api.py
- [x] T015 [P] [US1] Unit test for BoardService.create_board in tests/unit/test_board_service.py
- [x] T016 [P] [US1] Unit test for board validators in tests/unit/test_board_validators.py
- [x] T017 [P] [US1] Unit test for BoardRepository in tests/unit/test_board_repository.py
- [x] T018 [P] [US1] Unit test for ColumnRepository in tests/unit/test_column_repository.py
- [x] T019 [US1] Integration test for board creation in tests/integration/test_board_api.py

### Implementation for User Story 1

- [x] T020 [US1] Implement create_board method in BoardService in src/services/board_service.py
- [x] T021 [US1] Implement create method in BoardRepository in src/repositories/board_repository.py
- [x] T022 [US1] Implement create_columns method in ColumnRepository in src/repositories/column_repository.py
- [x] T023 [US1] Implement POST /boards endpoint in src/api/v1/boards.py
- [x] T024 [US1] Add board name validation in src/utils/board_validators.py
- [x] T025 [US1] Add board limit check (1 board per user) in src/services/board_service.py
- [x] T026 [US1] Add error handling for duplicate board names in src/services/board_service.py
- [x] T027 [US1] Add logging for board creation operations in src/services/board_service.py

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Просмотр списка своих досок (Priority: P2)

**Goal**: Пользователь может просмотреть список всех созданных им досок с количеством задач в каждой колонке

**Independent Test**: Создать несколько досок и проверить, что все они отображаются в списке с правильной информацией

### Tests for User Story 2

- [x] T028 [P] [US2] Contract test for GET /boards in tests/contract/test_board_api.py
- [x] T029 [P] [US2] Unit test for BoardService.list_boards in tests/unit/test_board_service.py
- [x] T030 [US2] Integration test for listing boards in tests/integration/test_board_api.py

### Implementation for User Story 2

- [x] T031 [US2] Implement list_boards method in BoardService in src/services/board_service.py
- [x] T032 [US2] Implement get_by_user_id method in BoardRepository in src/repositories/board_repository.py
- [x] T033 [US2] Implement GET /boards endpoint in src/api/v1/boards.py
- [x] T034 [US2] Add task count aggregation for columns in src/repositories/board_repository.py
- [x] T035 [US2] Add logging for board listing operations in src/services/board_service.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Удаление доски (Priority: P3)

**Goal**: Пользователь может удалить созданную им доску с каскадным удалением всех связанных данных

**Independent Test**: Создать доску с задачами и проверить, что после удаления доска и все связанные данные недоступны

### Tests for User Story 3

- [x] T036 [P] [US3] Contract test for DELETE /boards/{id} in tests/contract/test_board_api.py
- [x] T037 [P] [US3] Unit test for BoardService.delete_board in tests/unit/test_board_service.py
- [x] T038 [US3] Integration test for board deletion in tests/integration/test_board_api.py

### Implementation for User Story 3

- [x] T039 [US3] Implement delete_board method in BoardService in src/services/board_service.py
- [x] T040 [US3] Implement delete method in BoardRepository in src/repositories/board_repository.py
- [x] T041 [US3] Implement DELETE /boards/{id} endpoint in src/api/v1/boards.py
- [x] T042 [US3] Add ownership check before deletion in src/services/board_service.py
- [x] T043 [US3] Add logging for board deletion operations in src/services/board_service.py

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Additional API Endpoint - Get Board by ID

**Goal**: Пользователь может получить детальную информацию о конкретной доске

**Independent Test**: Создать доску и получить её по ID, проверив все данные

### Tests for Get Board

- [x] T044 [P] Contract test for GET /boards/{id} in tests/contract/test_board_api.py
- [x] T045 [P] Unit test for BoardService.get_board in tests/unit/test_board_service.py
- [x] T046 Integration test for getting board by ID in tests/integration/test_board_api.py

### Implementation for Get Board

- [x] T047 Implement get_board method in BoardService in src/services/board_service.py
- [x] T048 Implement get_by_id method in BoardRepository in src/repositories/board_repository.py
- [x] T049 Implement GET /boards/{id} endpoint in src/api/v1/boards.py
- [x] T050 Add ownership check for get_board in src/services/board_service.py

**Checkpoint**: All API endpoints are now functional

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T051 [P] Update README.md with board management API documentation
- [x] T052 [P] Update .roo/rules/specify-rules.md with board management technologies
- [x] T053 Run all tests and ensure 80% coverage target is met
- [x] T054 Run quickstart.md validation to ensure all examples work
- [x] T055 Add API documentation for board endpoints in src/api/v1/boards.py
- [x] T056 Performance optimization for board listing queries
- [x] T057 Security review for board ownership checks
- [x] T058 Code cleanup and refactoring

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3 → Get Board)
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Depends on US1 for board creation, but independently testable
- **User Story 3 (P3)**: Can start after Foundational (Phase 2) - Depends on US1 for board creation, but independently testable
- **Get Board**: Can start after Foundational (Phase 2) - Depends on US1 for board creation, but independently testable

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks (T001-T003) can run in parallel
- All Foundational tasks marked [P] (T004-T011) can run in parallel within Phase 2
- Once Foundational phase completes, all user stories can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Terminal 1: Write contract test
- [ ] T014 [P] [US1] Contract test for POST /boards in tests/contract/test_board_api.py

# Terminal 2: Write unit tests (parallel)
- [ ] T015 [P] [US1] Unit test for BoardService.create_board in tests/unit/test_board_service.py
- [ ] T016 [P] [US1] Unit test for board validators in tests/unit/test_board_validators.py
- [ ] T017 [P] [US1] Unit test for BoardRepository in tests/unit/test_board_repository.py
- [ ] T018 [P] [US1] Unit test for ColumnRepository in tests/unit/test_column_repository.py

# Terminal 3: Write integration test (after unit tests)
- [ ] T019 [US1] Integration test for board creation in tests/integration/test_board_api.py

# Terminal 4: Implement (after tests fail)
- [ ] T020 [US1] Implement create_board method in BoardService in src/services/board_service.py
- [ ] T021 [US1] Implement create method in BoardRepository in src/repositories/board_repository.py
- [ ] T022 [US1] Implement create_columns method in ColumnRepository in src/repositories/column_repository.py
- [ ] T023 [US1] Implement POST /boards endpoint in src/api/v1/boards.py
- [ ] T024 [US1] Add board name validation in src/utils/board_validators.py
- [ ] T025 [US1] Add board limit check (1 board per user) in src/services/board_service.py
- [ ] T026 [US1] Add error handling for duplicate board names in src/services/board_service.py
- [ ] T027 [US1] Add logging for board creation operations in src/services/board_service.py
```

---

## Implementation Strategy

### MVP Scope (Recommended First Delivery)

**MVP = User Story 1 only** (T014-T027)

This delivers:
- Board creation with predefined columns
- Board name validation
- Board limit enforcement (1 per user)
- Duplicate name prevention

**Why this MVP?**
- Users can start organizing tasks immediately
- Core data model is established
- Foundation for all other stories
- Independently testable and deliverable

### Incremental Delivery

1. **Sprint 1**: MVP (US1) - Board creation
2. **Sprint 2**: US2 - Board listing
3. **Sprint 3**: US3 - Board deletion
4. **Sprint 4**: Get Board endpoint + Polish

Each sprint delivers a complete, independently testable feature increment.

---

## Task Summary

- **Total Tasks**: 58
- **Setup Phase**: 3 tasks
- **Foundational Phase**: 10 tasks
- **User Story 1**: 14 tasks (6 tests + 8 implementation)
- **User Story 2**: 8 tasks (3 tests + 5 implementation)
- **User Story 3**: 8 tasks (3 tests + 5 implementation)
- **Get Board**: 7 tasks (3 tests + 4 implementation)
- **Polish Phase**: 8 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel

**Independent Test Criteria**:
- US1: Create board and verify 5 columns exist with correct names
- US2: Create multiple boards and verify all appear in list
- US3: Create board with tasks, delete, verify all data removed
- Get Board: Create board, fetch by ID, verify all data correct

**Suggested MVP Scope**: User Story 1 (T014-T027) - 14 tasks

---

## Format Validation

✅ All tasks follow the checklist format:
- Checkbox: `- [ ]` present
- Task ID: Sequential (T001-T058)
- [P] marker: Present for parallelizable tasks
- [Story] label: Present for user story phase tasks (US1, US2, US3)
- Description: Clear action with exact file path