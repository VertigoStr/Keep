# Data Model: User Authentication and Registration

**Feature**: 001-user-auth  
**Date**: 2026-03-02  
**Database**: PostgreSQL

## Entities

### User

Represents a registered user in the system.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | User's email address |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt hashed password |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Last update timestamp |

**Validation Rules**:
- Email: must match standard format (user@domain.com), trimmed of leading/trailing whitespace
- Password: minimum 8 characters, at least 1 uppercase, 1 digit, 1 special character
- Email uniqueness: enforced at database level with UNIQUE constraint

**State Transitions**:
```
[New] → [Registered] (after successful registration)
[Registered] → [Active] (after first login)
[Active] → [Inactive] (after logout - session state, not user state)
```

### FailedLoginAttempt

Tracks failed login attempts for brute force protection.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier |
| email | VARCHAR(255) | NOT NULL, INDEX | Email used in attempt |
| ip_address | VARCHAR(45) | NOT NULL | Client IP address (IPv4/IPv6) |
| timestamp | TIMESTAMP | NOT NULL, DEFAULT NOW() | Attempt timestamp |
| user_agent | VARCHAR(500) | NULL | Client user agent string |

**Validation Rules**:
- Email: must be valid format
- IP address: must be valid IPv4 or IPv6 format

**Cleanup Policy**:
- Records older than 24 hours can be automatically cleaned up

### Session

Represents an active user session (JWT token metadata).

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PRIMARY KEY, NOT NULL | Unique identifier |
| user_id | UUID | NOT NULL, FOREIGN KEY → User.id | Associated user |
| token_hash | VARCHAR(255) | NOT NULL, UNIQUE | Hashed JWT token |
| expires_at | TIMESTAMP | NOT NULL | Token expiration time |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Session creation timestamp |

**Validation Rules**:
- Expires at: must be in the future (24 hours from creation)
- Token hash: SHA-256 hash of JWT token

**State Transitions**:
```
[New] → [Active] (after login)
[Active] → [Expired] (after 24 hours)
[Active] → [Terminated] (after logout)
```

## Relationships

```
User (1) ────────< (N) FailedLoginAttempt
User (1) ────────< (N) Session
```

## Indexes

| Table | Index | Type | Purpose |
|-------|-------|------|---------|
| users | idx_users_email | UNIQUE | Email uniqueness and lookup |
| failed_login_attempts | idx_failed_attempts_email | B-Tree | Rate limiting by email |
| failed_login_attempts | idx_failed_attempts_timestamp | B-Tree | Cleanup old records |
| sessions | idx_sessions_user_id | B-Tree | User session lookup |
| sessions | idx_sessions_token_hash | UNIQUE | Token validation |

## Database Schema (SQL)

```sql
-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);

-- Failed login attempts table
CREATE TABLE failed_login_attempts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_agent VARCHAR(500)
);

CREATE INDEX idx_failed_attempts_email ON failed_login_attempts(email);
CREATE INDEX idx_failed_attempts_timestamp ON failed_login_attempts(timestamp);

-- Sessions table
CREATE TABLE sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_sessions_user_id ON sessions(user_id);
CREATE INDEX idx_sessions_token_hash ON sessions(token_hash);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for users table
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

## Data Access Patterns

### User Repository
- `create_user(email, password_hash)` → User
- `get_user_by_email(email)` → User | None
- `get_user_by_id(user_id)` → User | None
- `email_exists(email)` → bool

### Failed Login Attempt Repository
- `create_attempt(email, ip_address, user_agent)` → FailedLoginAttempt
- `count_recent_attempts(email, minutes)` → int
- `cleanup_old_attempts(hours)` → int (deleted count)

### Session Repository
- `create_session(user_id, token_hash, expires_at)` → Session
- `get_session_by_token_hash(token_hash)` → Session | None
- `delete_session(session_id)` → bool
- `delete_user_sessions(user_id)` → int (deleted count)
- `cleanup_expired_sessions()` → int (deleted count)

## Security Considerations

1. **Password Storage**: Always use bcrypt with work factor >= 12
2. **Email Storage**: Store in lowercase for case-insensitive comparison
3. **Token Storage**: Store SHA-256 hash of JWT token, not the token itself
4. **PII**: Email is personally identifiable information - handle according to privacy policies
5. **Cleanup**: Implement automated cleanup of old failed attempts and expired sessions