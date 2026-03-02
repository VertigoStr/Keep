# Data Model: Task Management

**Feature**: 002-task-management
**Date**: 2026-03-02
**Database**: PostgreSQL

## Entities

### Task

Represents a task created by a user in the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY, NOT NULL, AUTO INCREMENT | Unique identifier |
| user_id | INTEGER | NOT NULL, FOREIGN KEY → User.id | Owner of the task |
| title | VARCHAR(255) | NOT NULL | Task title |
| description | VARCHAR(5000) | NOT NULL, DEFAULT '' | Task description (0-5000 chars) |
| due_date | DATE | NOT NULL | Due date in YYYY-MM-DD format |
| status | VARCHAR(50) | NOT NULL | Task status from predefined list |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Task creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Validation Rules**:
- Title: minimum 1 character, maximum 255 characters
- Description: minimum 0 characters, maximum 5000 characters
- Due date: valid date in YYYY-MM-DD format (past dates allowed)
- Status: must be one of predefined values ("к выполнению", "в работу", "возникла проблема", "сделано", "отмена")
- User ownership: user_id must reference existing user

**Status Values**:
```python
class TaskStatus(str, Enum):
    TODO = "к выполнению"
    IN_PROGRESS = "в работу"
    HAS_ISSUE = "возникла проблема"
    DONE = "сделано"
    CANCELLED = "отмена"
```

**State Transitions**:
```
Any status can transition to any other status (no restrictions)
```

## Relationships

```
User (1) ────────< (N) Task
```

- One user can have many tasks
- Each task belongs to exactly one user
- Cascade delete: when user is deleted, all their tasks are deleted

## Indexes

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| tasks | idx_tasks_user_id | B-Tree | User task lookup |
| tasks | idx_tasks_status | B-Tree | Status filtering (future use) |
| tasks | idx_tasks_due_date | B-Tree | Due date filtering (future use) |

## Database Schema (SQL)

```sql
-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description VARCHAR(5000) NOT NULL DEFAULT '',
    due_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_tasks_user_id ON tasks(user_id);
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due_date ON tasks(due_date);

-- Trigger to update updated_at timestamp
CREATE TRIGGER update_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Data Access Patterns

### Task Repository

- `create_task(user_id, title, description, due_date, status)` → Task
- `get_task_by_id(task_id)` → Task | None
- `get_user_tasks(user_id)` → List[Task]
- `update_task(task_id, **kwargs)` → Task | None
- `delete_task(task_id)` → bool
- `task_exists(task_id)` → bool
- `is_task_owner(task_id, user_id)` → bool

## Security Considerations

1. **Ownership Enforcement**: All repository methods must verify user ownership before allowing access
2. **SQL Injection**: Use parameterized queries (SQLAlchemy handles this)
3. **Data Privacy**: Task data is user-specific, ensure proper access control
4. **Cascade Delete**: Tasks are automatically deleted when user is deleted

## Integration with Existing Models

### User Model (from 001-user-auth)

The Task model references the existing User model:

```python
# Existing User model (simplified)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### Relationship Definition

```python
# Task model with relationship
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(String(5000), nullable=False, default="")
    due_date = Column(Date, nullable=False)
    status = Column(String(50), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", backref="tasks")
```

## Migration

New migration file: `alembic/versions/003_add_tasks.py`

This migration will:
1. Create the `tasks` table
2. Create indexes for user_id, status, and due_date
3. Add trigger for updated_at timestamp

## Performance Considerations

1. **Indexing**: Indexes on user_id ensure fast lookup of user's tasks
2. **Pagination**: For large task lists, implement pagination in repository methods
3. **Query Optimization**: Use SELECT only needed fields when listing tasks
4. **Connection Pooling**: SQLAlchemy connection pool handles concurrent requests

## Future Extensions

The data model is designed to support future enhancements:
- Task categories/tags (add category_id foreign key)
- Task priorities (add priority field)
- Task dependencies (add parent_task_id foreign key)
- Task comments (add comments table with task_id foreign key)
- Task attachments (add attachments table with task_id foreign key)