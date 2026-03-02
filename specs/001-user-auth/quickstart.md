# Quickstart: User Authentication and Registration

**Feature**: 001-user-auth  
**Date**: 2026-03-02

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- pip (Python package manager)

## Installation

### 1. Clone and Setup

```bash
cd /path/to/project
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trello

# JWT Secret (generate with: openssl rand -hex 32)
JWT_SECRET=your-secret-key-here

# JWT Expiration (in seconds, 24 hours = 86400)
JWT_EXPIRATION_SECONDS=86400

# Bcrypt Work Factor (recommended: 12)
BCRYPT_ROUNDS=12

# Application
APP_NAME=Trello Auth
APP_ENV=development
DEBUG=True
```

### 4. Database Setup

```bash
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

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### Register a New User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!",
    "password_confirm": "SecurePass123!"
  }'
```

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2026-03-02T10:00:00Z"
}
```

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123!"
  }' \
  -c cookies.txt
```

**Response**:
```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

### Get Current User

```bash
curl -X GET http://localhost:8000/api/v1/auth/me \
  -b cookies.txt
```

### Logout

```bash
curl -X POST http://localhost:8000/api/v1/auth/logout \
  -b cookies.txt
```

## Testing

### Run All Tests

```bash
pytest
```

### Run with Coverage

```bash
pytest --cov=src --cov-report=html
```

### Run Specific Test File

```bash
pytest tests/unit/test_password_service.py
```

## Project Structure

```
src/
├── main.py                 # FastAPI application entry point
├── config.py               # Configuration settings
├── models/
│   ├── user.py            # User SQLAlchemy model
│   ├── session.py         # Session SQLAlchemy model
│   └── failed_login.py    # FailedLoginAttempt SQLAlchemy model
├── schemas/
│   ├── user.py            # Pydantic schemas for User
│   └── auth.py            # Pydantic schemas for Auth requests/responses
├── services/
│   ├── auth_service.py    # Authentication business logic
│   ├── password_service.py # Password hashing/validation
│   ├── rate_limit_service.py # Rate limiting logic
│   └── logging_service.py # Logging logic
├── repositories/
│   ├── user_repository.py # User data access
│   ├── session_repository.py # Session data access
│   └── failed_login_repository.py # Failed login data access
├── api/
│   └── v1/
│       └── auth.py        # Auth API endpoints
└── utils/
    ├── security.py        # JWT token utilities
    └── validators.py      # Custom validators

tests/
├── unit/
│   ├── test_password_service.py
│   ├── test_auth_service.py
│   └── test_validators.py
├── integration/
│   └── test_auth_api.py
└── contract/
    └── test_api_contract.py

alembic/
├── versions/              # Database migration files
└── env.py                 # Alembic configuration
```

## Development Workflow

### Adding a New Feature

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement the feature
3. Write tests (unit + integration)
4. Ensure 80%+ test coverage
5. Run tests: `pytest`
6. Commit changes: `git commit -m "feat: add your feature"`
7. Push and create PR

### Code Style

- Follow PEP8
- Use snake_case for variables and functions
- Max line length: 120 characters
- Document all public methods and classes

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Troubleshooting

### Database Connection Error

```
Error: could not connect to server
```

**Solution**: Ensure PostgreSQL is running and DATABASE_URL is correct.

### JWT Secret Not Set

```
Error: JWT_SECRET environment variable not set
```

**Solution**: Add JWT_SECRET to your `.env` file.

### Rate Limiting Issues

If you're locked out during development, clear the failed login attempts:

```bash
# Connect to database
psql trello

# Clear failed attempts
DELETE FROM failed_login_attempts;
```

## Production Deployment

### Environment Variables

Set `APP_ENV=production` and `DEBUG=False` in production.

### Security Checklist

- [ ] Use strong JWT_SECRET (generate with `openssl rand -hex 32`)
- [ ] Enable HTTPS
- [ ] Set secure cookie flags
- [ ] Configure CORS properly
- [ ] Enable rate limiting
- [ ] Set up monitoring and logging
- [ ] Regular security updates

### Performance Tuning

- Use connection pooling for PostgreSQL
- Enable query caching
- Configure proper indexes
- Use CDN for static assets (if applicable)

## Support

For issues or questions, please refer to:
- API Documentation: `http://localhost:8000/docs`
- Project Repository: [link to repo]
- Team: [contact information]