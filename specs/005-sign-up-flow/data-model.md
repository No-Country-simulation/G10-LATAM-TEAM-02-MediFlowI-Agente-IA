# Data Model: Sign Up Flow

This document details the schema changes required in the PostgreSQL database (via Alembic/SQLAlchemy) to support the Sign Up flow.

## 1. `users` Table

The primary entity for authentication and authorization.

### Columns

| Name | Type | Constraints | Description |
|------|------|-------------|-------------|
| `id` | `UUID` | Primary Key, Default: `uuid4()` | Unique identifier for the user. |
| `nombre` | `VARCHAR(100)` | Not Null | First name(s). |
| `apellidos` | `VARCHAR(100)` | Not Null | Last name(s). |
| `telefono` | `VARCHAR(20)` | Not Null | Phone number. |
| `correo` | `VARCHAR(255)` | Not Null, Unique, Index | Email address used for login. |
| `hashed_password` | `VARCHAR(255)` | Not Null | Securely hashed password (bcrypt). |
| `status` | `VARCHAR(20)` | Not Null, Default: `'PENDING'` | User status (`PENDING`, `ACTIVE`, `INACTIVE`). New signups are `PENDING`. |
| `role` | `VARCHAR(50)` | Not Null, Default: `'OPERADOR'` | Role assignment (e.g., `OPERADOR`, `COORDINADOR`, `ADMINISTRADOR`). |
| `especialidad_medica` | `VARCHAR(100)` | Nullable | Medical specialty, if applicable. |
| `created_at` | `TIMESTAMP` | Not Null, Default: `now()` | Record creation timestamp. |
| `updated_at` | `TIMESTAMP` | Not Null, Default: `now()` | Record last update timestamp. |

### Database Constraints & Indexes

- `uq_users_correo`: Unique constraint on `correo` to prevent duplicate registrations.
- Check constraint on `status` to ensure it only takes valid values.

### State Transitions

- **Creation**: User registers via `/api/auth/signup` $\rightarrow$ `status` is set to `'PENDING'`.
- **Approval** *(Out of scope for this feature)*: Admin approves the user $\rightarrow$ `status` changes to `'ACTIVE'`.
