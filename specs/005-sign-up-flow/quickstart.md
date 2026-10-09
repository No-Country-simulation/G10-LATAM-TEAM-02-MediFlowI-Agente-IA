# Quickstart: Validation Guide for Sign Up Flow

This guide outlines how to manually validate the Sign Up feature once implemented.

## Prerequisites

- Backend environment running (`uvicorn app.main:app --reload`).
- PostgreSQL database running (`docker-compose up -d db`) and migrations applied (`alembic upgrade head`).
- Frontend development server running (`npm run dev`).

## 1. Validating the UI states

1. Navigate to `http://localhost:5173/signup` (or the configured frontend port).
2. Ensure the form matches the Figma "reposo" state.
3. Click on the email input, enter "invalid-email", and click outside. Verify the inline error appears.
4. Fill in the rest of the form with valid data, but make the "Contraseña" and "Confirmar contraseña" fields mismatch. Verify the inline mismatch error appears.

## 2. Validating Backend Validations & Duplicates

1. Submit the form with valid data for a new user.
2. Verify the submit button shows a loading spinner during the request.
3. Upon success, verify the "Registro exitoso" alert appears.
4. Open your PostgreSQL client and query the `users` table to verify the user was created with a hashed password and `status = 'PENDING'`.
   ```sql
   SELECT id, correo, status, hashed_password FROM users WHERE correo = 'test@example.com';
   ```
5. Without refreshing, try to submit the form again (or refresh and use the exact same email).
6. Verify the inline error "El correo ya está registrado" appears, driven by the `409 Conflict` response.

## 3. Validating Automated Tests

Run the backend unit and E2E tests:
```bash
pytest tests/api/v1/test_auth.py -v
```

Run the frontend component tests:
```bash
npm run test -- SignUpForm
```

