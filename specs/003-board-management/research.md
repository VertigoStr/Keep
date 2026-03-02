# Research: Board Management

**Feature**: 003-board-management
**Date**: 2026-03-02
**Status**: Complete

## Overview

Этот документ содержит результаты исследования технических решений для реализации функциональности управления досками. Все вопросы из Technical Context были разрешены.

---

## Research Topics

### 1. SQLAlchemy Models for Board and Column

**Decision**: Использовать SQLAlchemy ORM с declarative base для моделей Board и Column.

**Rationale**:
- Проект уже использует SQLAlchemy для моделей User, Session, FailedLogin
- ORM обеспечивает типобезопасность и автоматическую генерацию SQL
- Поддержка миграций через Alembic уже настроена
- Легкая интеграция с Pydantic для валидации

**Alternatives considered**:
- Raw SQL: Отклонено из-за отсутствия типобезопасности и сложности поддержки
- SQLModel: Отклонено, так как SQLAlchemy уже используется в проекте

**Implementation details**:
```python
# models/board.py
class Board(Base):
    __tablename__ = "boards"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="boards")
    columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_board_name'),
    )

# models/column.py
class Column(Base):
    __tablename__ = "columns"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    order = Column(Integer, nullable=False)
    board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)

    board = relationship("Board", back_populates="columns")
    tasks = relationship("Task", back_populates="column", cascade="all, delete-orphan")
```

---

### 2. Cascade Deletion in SQLAlchemy

**Decision**: Использовать каскадное удаление на уровне базы данных (ON DELETE CASCADE) и на уровне ORM (cascade="all, delete-orphan").

**Rationale**:
- Обеспечивает целостность данных при удалении доски
- Удаляет все колонки и задачи автоматически
- Предотвращает появление "сиротских" записей
- SQLAlchemy поддерживает оба уровня каскадирования

**Alternatives considered**:
- Soft delete (is_deleted flag): Отклонено, так как спецификация требует hard delete
- Ручное удаление в транзакции: Отклонено из-за сложности и риска ошибок

**Implementation details**:
```python
# На уровне базы данных (через ForeignKey)
board_id = Column(Integer, ForeignKey("boards.id", ondelete="CASCADE"), nullable=False)

# На уровне ORM (через relationship)
columns = relationship("Column", back_populates="board", cascade="all, delete-orphan")
```

---

### 3. Board Name Validation

**Decision**: Использовать Pydantic для валидации названия доски с regex-паттерном.

**Rationale**:
- Pydantic уже используется в проекте для валидации (schemas/auth.py)
- Автоматическая генерация ошибок валидации
- Поддержка кастомных валидаторов
- Интеграция с FastAPI для автоматической документации

**Alternatives considered**:
- Валидация в сервисном слое: Отклонено, так как Pydantic более декларативен
- Валидация на уровне базы данных (CHECK constraint): Отклонено, так как не даёт понятных сообщений об ошибках

**Implementation details**:
```python
# schemas/board.py
from pydantic import BaseModel, Field, field_validator
import re

class BoardCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        pattern = r'^[\p{L}\p{N}\s.,!?\-:;]+$'
        if not re.match(pattern, v):
            raise ValueError(
                'Название может содержать только буквы, цифры, '
                'пробелы и символы .,!?-:;'
            )
        return v.strip()
```

---

### 4. Unique Constraint on Composite Key (user_id + name)

**Decision**: Использовать SQLAlchemy UniqueConstraint на составной ключ (user_id, name).

**Rationale**:
- Обеспечивает уникальность названия доски в пределах одного пользователя
- Предотвращает race conditions при одновременном создании досок
- Автоматическая обработка на уровне базы данных
- SQLAlchemy поддерживает это через __table_args__

**Alternatives considered**:
- Проверка в приложении перед созданием: Отклонено из-за race conditions
- Триггер базы данных: Отклонено из-за сложности и переносимости

**Implementation details**:
```python
class Board(Base):
    # ... поля ...

    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_board_name'),
    )
```

**Error handling**:
```python
# В сервисном слое
try:
    board = Board(name=data.name, user_id=user_id)
    db.add(board)
    db.commit()
except IntegrityError as e:
    if 'uq_user_board_name' in str(e):
        raise BoardAlreadyExistsError(
            "Доска с таким названием уже существует"
        )
    raise
```

---

### 5. Integration with Existing Models

**Decision**: Добавить обратные связи (back_populates) в существующие модели User и Task.

**Rationale**:
- Обеспечивает навигацию между связанными сущностями
- Соответствует принципам ORM
- Позволяет использовать eager loading для оптимизации запросов

**Alternatives considered**:
- Без обратных связей: Отклонено, так как усложняет навигацию
- Отдельные запросы для получения связанных данных: Отклонено из-за N+1 проблемы

**Implementation details**:
```python
# models/user.py - добавить
boards = relationship("Board", back_populates="user", cascade="all, delete-orphan")

# models/task.py - добавить (из 002-task-management)
column_id = Column(Integer, ForeignKey("columns.id", ondelete="SET NULL"), nullable=True)
column = relationship("Column", back_populates="tasks")
```

---

### 6. Board Limit per User (1 board)

**Decision**: Проверять лимит досок на уровне сервиса перед созданием.

**Rationale**:
- Простая реализация
- Понятные сообщения об ошибках
- Легко тестируется

**Alternatives considered**:
- CHECK constraint на уровне базы данных: Отклонено, так как требует подзапроса
- Триггер базы данных: Отклонено из-за сложности

**Implementation details**:
```python
# services/board_service.py
async def create_board(user_id: int, data: BoardCreate) -> Board:
    # Проверка лимита досок
    existing_count = await board_repository.count_by_user(user_id)
    if existing_count >= 1:
        raise BoardLimitExceededError(
            "Достигнут лимит досок (максимум 1)"
        )

    # Создание доски
    board = await board_repository.create(user_id=user_id, name=data.name)

    # Создание предопределённых колонок
    predefined_columns = [
        ("К выполнению", 1),
        ("В работу", 2),
        ("Возникла проблема", 3),
        ("Сделано", 4),
        ("Отмена", 5),
    ]
    for name, order in predefined_columns:
        await column_repository.create(board_id=board.id, name=name, order=order)

    return board
```

---

### 7. API Endpoint Design

**Decision**: RESTful API с ресурсоориентированным дизайном.

**Rationale**:
- Соответствует принципам REST
- Легко документируется через OpenAPI/Swagger
- Интуитивно понятен для разработчиков

**Endpoints**:
```
POST   /api/v1/boards          - Создать доску
GET    /api/v1/boards          - Получить список досок текущего пользователя
GET    /api/v1/boards/{id}     - Получить доску по ID
DELETE /api/v1/boards/{id}     - Удалить доску
```

**Alternatives considered**:
- GraphQL: Отклонено, так как избыточно для простого CRUD
- gRPC: Отклонено, так как проект использует HTTP/REST

---

### 8. Testing Strategy

**Decision**: Трёхуровневое тестирование: unit, integration, contract.

**Rationale**:
- Unit тесты для бизнес-логики (services)
- Integration тесты для API endpoints
- Contract тесты для проверки соответствия спецификации
- Соответствует существующей структуре проекта

**Test coverage target**: 80%

**Implementation details**:
```python
# tests/unit/test_board_service.py
@pytest.mark.asyncio
async def test_create_board_success():
    # ...

# tests/integration/test_board_api.py
@pytest.mark.asyncio
async def test_create_board_endpoint(client, auth_headers):
    # ...

# tests/contract/test_board_api.py
def test_board_api_contract():
    # Проверка соответствия OpenAPI спецификации
```

---

## Summary

Все технические решения для реализации функциональности управления досками определены. Выбранные подходы соответствуют существующей архитектуре проекта, конституции и лучшим практикам разработки на Python/FastAPI.

**Key decisions**:
1. SQLAlchemy ORM для моделей Board и Column
2. Каскадное удаление на уровне БД и ORM
3. Pydantic для валидации названий досок
4. UniqueConstraint на (user_id, name)
5. Обратные связи в существующих моделях
6. Проверка лимита досок в сервисном слое
7. RESTful API дизайн
8. Трёхуровневое тестирование

**Next steps**: Phase 1 - Generate data-model.md, contracts/, quickstart.md