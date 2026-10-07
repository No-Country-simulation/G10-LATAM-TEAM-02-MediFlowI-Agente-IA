# API Contract: Sign Up Endpoint

## POST `/api/auth/signup`

Creates a new user account in a "Pending" state.

### Request Body (`application/json`)

```json
{
  "nombre": "Alex Jordan",
  "apellidos": "Castañeda",
  "telefono": "+525551523056",
  "correo": "alex.jordan@gmail.com",
  "password": "Strong#Password123"
}
```

#### Field Validations (Pydantic Schema)

- `nombre`: string, min_length: 1, max_length: 100
- `apellidos`: string, min_length: 1, max_length: 100
- `telefono`: string, regex validation for common phone formats (e.g., `^\+?[1-9]\d{1,14}$`), max_length: 20
- `correo`: string, valid email format (using Pydantic `EmailStr`)
- `password`: string, minimum 8 characters, must contain at least one special character, one uppercase letter, and one number.

### Responses

#### 201 Created

Returns a summary of the created user (omitting sensitive data like password hashes).

```json
{
  "message": "User registered successfully. Pending admin approval.",
  "user": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "nombre": "Alex Jordan",
    "apellidos": "Castañeda",
    "correo": "alex.jordan@gmail.com",
    "status": "INACTIVO"
  }
}
```

#### 400 Bad Request

Validation errors from Pydantic (e.g., weak password, invalid email format, missing fields).

```json
{
  "detail": [
    {
      "loc": ["body", "correo"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

#### 409 Conflict

Email address is already registered.

```json
{
  "detail": "El correo ya está registrado."
}
```

#### 500 Internal Server Error

Unexpected server failure (triggers global alert in UI).

```json
{
  "detail": "Ocurrió un error inesperado al procesar la solicitud en el servidor."
}
```

