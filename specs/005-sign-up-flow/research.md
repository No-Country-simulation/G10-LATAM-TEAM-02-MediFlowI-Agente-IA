# Phase 0: Research & Technical Decisions

## 1. Password Hashing Library for FastAPI Backend

**Decision**: Use the `bcrypt` library directly instead of `passlib`.

**Rationale**:
- **Why it was needed**: The backend needs to securely hash passwords before storing them in PostgreSQL (FR-008). No hashing library was present in `backend/pyproject.toml`.
- **Why `bcrypt` directly**: `passlib` has been the standard in the FastAPI ecosystem for years, but it is currently unmaintained and causes warnings with newer Python versions (3.11+). Using the `bcrypt` package directly is the modern best practice recommended for new Python projects.
- **Implementation Note**: Since hashing is CPU-bound, `bcrypt.hashpw` and `bcrypt.checkpw` should be run in a thread pool (e.g., using `run_in_threadpool` from `starlette.concurrency` or standard asyncio threading) to avoid blocking the async event loop, although for a simple endpoint the direct call is often acceptable.

**Alternatives considered**:
- `passlib[bcrypt]`: Rejected due to lack of active maintenance.
- `argon2-cffi`: A strong modern alternative, but `bcrypt` is simpler, widely understood, and sufficient for this project's security requirements.

## 2. API Error Response Structure

**Decision**: Use standard FastAPI HTTPExceptions with Pydantic models for structured error responses.

**Rationale**:
- **Why it was needed**: The frontend needs specific inline error messages (FR-004) and global alerts based on backend responses.
- **Implementation**: For duplicate emails, the backend will return a `409 Conflict` with `{"detail": "El correo ya está registrado"}`. The frontend `auth.api.ts` service will intercept this and throw a typed error that the `SignUpForm` component can catch and map to the specific email input field.

**Alternatives considered**:
- Returning `200 OK` with a custom error payload: Rejected as it violates HTTP semantics and the project's Golden Rule #3 regarding standard HTTP codes.

