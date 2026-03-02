# Trello Auth API

User Authentication and Registration API built with FastAPI, PostgreSQL, and JWT tokens.

## Features

- User registration with email and password
- Password complexity validation (8+ chars, 1 uppercase, 1 digit, 1 special char)
- User authentication with JWT tokens
- Brute force protection (3 attempts per 15 minutes)
- Session management with 24-hour expiration
- User logout
- Get current user information

## Tech Stack

- **Language**: Python 3.11
- **Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with HTTP-only cookies
- **Password Hashing**: bcrypt (work factor 12)
- **Rate Limiting**: slowapi
- **Testing**: pytest, pytest-asyncio, httpx

## Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+

### Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

# Edit .env with your configuration
# DATABASE_URL=postgresql://user:password@localhost:5432/trello
# JWT_SECRET=your-secret-key-here

# Create database
createdb trello

# Run migrations
alembic upgrade head
```

## Running the Application

### Development Server

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

#### Register a new user

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

**Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2026-03-02T10:00:00Z"
}
```

#### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200 OK)**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

Sets `session_token` HTTP-only cookie.

#### Logout

```http
POST /api/v1/auth/logout
Cookie: session_token=<jwt_token>
```

**Response (200 OK)**:
```json
{
  "message": "Logged out successfully"
}
```

#### Get current user

```http
GET /api/v1/auth/me
Cookie: session_token=<jwt_token>
```

**Response (200 OK)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2026-03-02T10:00:00Z"
}
```

## Testing

### Run all tests

```bash
pytest
```

### Run with coverage

```bash
pytest --cov=src --cov-report=html
```

### Run specific test file

```bash
pytest tests/unit/test_password_service.py
```

### Run specific test

```bash
pytest tests/unit/test_password_service.py::TestPasswordService::test_hash_password
```

## Project Structure

```
src/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings
├── database.py             # Database session management
├── models/                 # SQLAlchemy models
│   ├── user.py            # User model
│   ├── session.py         # Session model
│   └── failed_login.py    # FailedLoginAttempt model
├── schemas/                # Pydantic schemas
│   └── auth.py            # Auth request/response schemas
├── services/               # Business logic
│   ├── auth_service.py    # Authentication service
│   ├── password_service.py # Password hashing
│   ├── rate_limit_service.py # Rate limiting
│   └── session_service.py # Session management
├── repositories/           # Data access layer
│   ├── user_repository.py
│   ├── session_repository.py
│   └── failed_login_repository.py
├── api/                    # API endpoints
│   └── v1/
│       └── auth.py        # Auth endpoints
├── utils/                  # Utilities
│   ├── security.py        # JWT utilities
│   ├── validators.py      # Input validators
│   └── logging.py         # Logging configuration
└── middleware/             # Middleware
    ├── error_handler.py   # Error handling
    └── security.py        # Security headers

tests/
├── conftest.py            # Pytest fixtures
├── unit/                  # Unit tests
├── integration/           # Integration tests
└── contract/              # Contract tests

alembic/                   # Database migrations
└── versions/
```

## Security

- Passwords are hashed using bcrypt with work factor 12
- JWT tokens are stored in HTTP-only cookies to prevent XSS attacks
- Rate limiting prevents brute force attacks (3 attempts per 15 minutes)
- Security headers are set on all responses
- CORS is configured appropriately

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection URL | `postgresql://user:password@localhost:5432/trello` |
| `JWT_SECRET` | Secret key for JWT signing | `your-secret-key-here` |
| `JWT_EXPIRATION_SECONDS` | JWT token expiration time | `86400` (24 hours) |
| `BCRYPT_ROUNDS` | Bcrypt work factor | `12` |
| `APP_NAME` | Application name | `Trello Auth` |
| `APP_ENV` | Environment (development/production) | `development` |
| `DEBUG` | Debug mode flag | `True` |

## Code Quality

- **PEP8 compliance**: Enforced via black, flake8, and mypy
- **Pre-commit hooks**: Configured for automatic code formatting and linting
- **Test coverage**: Target 80%+ coverage

## License

MIT