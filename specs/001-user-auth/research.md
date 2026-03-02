# Research: User Authentication and Registration

**Feature**: 001-user-auth  
**Date**: 2026-03-02  
**Status**: Complete

## Technology Decisions

### Password Hashing

**Decision**: bcrypt

**Rationale**: bcrypt является отраслевым стандартом для хеширования паролей. Он включает встроенную соль, имеет настраиваемый фактор стоимости (work factor) для защиты от брутфорса на GPU, и широко поддерживается в Python через библиотеку `bcrypt`. Альтернативы:
- argon2: более современный, но требует дополнительных зависимостей
- PBKDF2: встроен в Python, но менее устойчив к GPU-атакам

**Alternatives considered**:
- argon2: более современный алгоритм, победитель конкурса Password Hashing Competition, но требует компиляции C-расширений
- PBKDF2: встроен в Python (hashlib), но менее устойчив к атакам на GPU

### Session Management

**Decision**: JWT (JSON Web Tokens) with HTTP-only cookies

**Rationale**: JWT токены stateless и хорошо масштабируются. HTTP-only cookies защищают от XSS атак. FastAPI имеет встроенную поддержку через `fastapi.security`. Срок действия 24 часа соответствует требованиям спецификации.

**Alternatives considered**:
- Server-side sessions (Redis): более безопасны, но требуют дополнительной инфраструктуры
- LocalStorage: уязвим для XSS атак

### Database

**Decision**: PostgreSQL

**Rationale**: PostgreSQL является реляционной базой данных с поддержкой транзакций, что критично для аутентификации. Поддерживает JSON для расширяемости. Хорошо интегрируется с Python через SQLAlchemy.

**Alternatives considered**:
- SQLite: подходит для разработки, но не для продакшена с 1000+ concurrent requests
- MySQL: альтернатива, но PostgreSQL имеет более продвинутые возможности

### Rate Limiting

**Decision**: slowapi (FastAPI rate limiter)

**Rationale**: slowapi - это популярная библиотека для rate limiting в FastAPI. Поддерживает различные стратегии (IP, user) и хранилища (in-memory, Redis). Для блокировки на 15 минут после 3 неудачных попыток подходит идеально.

**Alternatives considered**:
- fastapi-limiter: альтернатива, но менее гибкая
- Nginx rate limiting: работает на уровне инфраструктуры, но сложнее в настройке

### Password Validation

**Decision**: Custom validator with regex

**Rationale**: Для требований (8+ символов, 1 заглавная, 1 цифра, 1 спецсимвол) достаточно регулярного выражения. Pydantic поддерживает валидацию через `@validator` декоратор.

**Alternatives considered**:
- password-strength: внешняя библиотека, но избыточна для простых требований

### Logging

**Decision**: Python logging module with structured logging

**Rationale**: Встроенный модуль `logging` соответствует требованиям PEP8. Для структурированного логирования можно использовать `structlog` или JSON формат. Логируем только неудачные попытки входа согласно спецификации.

**Alternatives considered**:
- ELK stack: избыточно для простого логирования
- Sentry: подходит для мониторинга ошибок, но не для всех событий

## Best Practices

### Security
- Всегда использовать HTTPS в продакшене
- Хешировать пароли с bcrypt (work factor >= 12)
- Использовать HTTP-only cookies для JWT токенов
- Валидировать все входные данные
- Логировать неудачные попытки входа для мониторинга

### Code Quality
- Следовать PEP8 (snake_case, max 120 chars)
- SOLID принципы: отдельные сервисы для аутентификации, валидации, логирования
- DRY: переиспользовать валидаторы и утилиты
- KISS: простые, понятные функции

### Testing
- Unit тесты для всех сервисов
- Интеграционные тесты для API endpoints
- Покрытие минимум 80%
- Тесты для граничных случаев (короткий пароль, неверный email и т.д.)

### Performance
- Кэширование валидированных email (Redis)
- Connection pooling для PostgreSQL
- Асинхронные операции (async/await в FastAPI)
- Индексы на email поле в базе данных

## Dependencies

```python
# Core
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
pydantic>=2.5.0
pydantic-settings>=2.1.0

# Database
sqlalchemy>=2.0.23
asyncpg>=0.29.0
alembic>=1.13.0

# Security
bcrypt>=4.1.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4

# Rate Limiting
slowapi>=0.1.9

# Testing
pytest>=7.4.3
pytest-asyncio>=0.21.1
httpx>=0.25.2
```

## Architecture Patterns

### Layered Architecture
```
API Layer (FastAPI routes)
    ↓
Service Layer (business logic)
    ↓
Repository Layer (data access)
    ↓
Database (PostgreSQL)
```

### Services
- `AuthService`: регистрация, вход, выход
- `PasswordService`: хеширование, валидация
- `RateLimitService`: защита от брутфорса
- `LoggingService`: логирование событий

### Models
- `User`: email, password_hash, created_at
- `FailedLoginAttempt`: email, ip_address, timestamp

## Open Questions Resolved

All technical unknowns from the specification have been resolved through this research phase. No NEEDS CLARIFICATION markers remain.