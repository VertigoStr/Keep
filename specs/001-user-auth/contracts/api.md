# API Contract: User Authentication and Registration

**Feature**: 001-user-auth  
**Date**: 2026-03-02  
**Protocol**: HTTP/REST  
**Content-Type**: application/json

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All protected endpoints require authentication via JWT token in HTTP-only cookie.

## Endpoints

### POST /auth/register

Register a new user account.

**Request**:
```http
POST /api/v1/auth/register
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!"
}
```

**Request Validation**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| email | string | Yes | Valid email format, trimmed, max 255 chars |
| password | string | Yes | Min 8 chars, 1 uppercase, 1 digit, 1 special char |
| password_confirm | string | Yes | Must match password |

**Response (201 Created)**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "created_at": "2026-03-02T10:00:00Z"
}
```

**Response (400 Bad Request)** - Validation errors:
```json
{
  "error": "validation_error",
  "message": "Password does not meet complexity requirements",
  "details": {
    "field": "password",
    "constraint": "minimum 8 characters, 1 uppercase, 1 digit, 1 special character"
  }
}
```

**Response (400 Bad Request)** - Passwords don't match:
```json
{
  "error": "validation_error",
  "message": "Passwords do not match"
}
```

**Response (400 Bad Request)** - Invalid email format:
```json
{
  "error": "validation_error",
  "message": "Invalid email format"
}
```

**Response (409 Conflict)** - Email already exists:
```json
{
  "error": "email_exists",
  "message": "User with this email already exists"
}
```

---

### POST /auth/login

Authenticate a user and create a session.

**Request**:
```http
POST /api/v1/auth/login
Content-Type: application/json
```

**Request Body**:
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Request Validation**:
| Field | Type | Required | Validation |
|-------|------|----------|------------|
| email | string | Yes | Valid email format, trimmed |
| password | string | Yes | Non-empty string |

**Response (200 OK)**:
```http
Set-Cookie: session_token=<jwt_token>; HttpOnly; Path=/; Max-Age=86400; SameSite=Strict
```

```json
{
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com"
  }
}
```

**Response (400 Bad Request)** - Missing fields:
```json
{
  "error": "validation_error",
  "message": "All fields are required"
}
```

**Response (401 Unauthorized)** - Invalid credentials:
```json
{
  "error": "invalid_credentials",
  "message": "Invalid email or password"
}
```

**Response (429 Too Many Requests)** - Rate limited:
```http
Retry-After: 900
```

```json
{
  "error": "too_many_attempts",
  "message": "Too many failed login attempts. Please try again in 15 minutes."
}
```

---

### POST /auth/logout

Terminate the current user session.

**Request**:
```http
POST /api/v1/auth/logout
Cookie: session_token=<jwt_token>
```

**Response (200 OK)**:
```http
Set-Cookie: session_token=; HttpOnly; Path=/; Max-Age=0; SameSite=Strict
```

```json
{
  "message": "Logged out successfully"
}
```

**Response (401 Unauthorized)** - Not authenticated:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

---

### GET /auth/me

Get current authenticated user information.

**Request**:
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

**Response (401 Unauthorized)** - Not authenticated:
```json
{
  "error": "unauthorized",
  "message": "Authentication required"
}
```

---

## Error Response Format

All error responses follow this structure:

```json
{
  "error": "error_code",
  "message": "Human-readable error message",
  "details": {
    "additional": "context"
  }
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| validation_error | 400 | Request validation failed |
| invalid_credentials | 401 | Invalid email or password |
| unauthorized | 401 | Authentication required |
| email_exists | 409 | Email already registered |
| too_many_attempts | 429 | Rate limit exceeded |
| internal_error | 500 | Internal server error |

---

## Rate Limiting

**Endpoint**: `/auth/login`  
**Limit**: 3 attempts per 15 minutes per email address  
**Response**: HTTP 429 with `Retry-After` header

---

## Security Headers

All responses include these security headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

---

## JWT Token Structure

```json
{
  "sub": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "iat": 1709376000,
  "exp": 1709462400
}
```

| Claim | Description |
|-------|-------------|
| sub | User ID (subject) |
| email | User email |
| iat | Issued at (Unix timestamp) |
| exp | Expiration time (Unix timestamp, 24 hours from iat) |