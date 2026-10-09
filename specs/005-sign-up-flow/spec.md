# Feature Specification: Sign Up Flow

**Feature Branch**: `[005-sign-up-flow]`

**Created**: 2026-10-07

**Status**: Draft

**Input**: User description: "Implementar el flujo completo de Sign Up (registro de usuarios) basado en las capturas de Figma adjuntas..."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Successful Registration Request (Priority: P1)

Users can request a new account by providing their personal information and securely setting a password, receiving immediate visual confirmation that their request was sent for approval.

**Why this priority**: Core entry point for new users to access the MediFlow platform.

**Independent Test**: Can be fully tested by submitting valid data through the UI form and verifying the database record and 201 Created response.

**Acceptance Scenarios**:

1. **Given** a user is on the Sign Up page, **When** they fill in valid details (Nombre, Apellidos, Teléfono, Correo, Contraseña, Confirmar Contraseña) and submit, **Then** they see a success confirmation and their account is created in the database.
2. **Given** the form is submitting, **When** the request is in flight, **Then** the submit button enters a loading state (spinner) and is disabled to prevent duplicate submissions.

---

### User Story 2 - Validation and Error Handling (Priority: P1)

Users receive clear, immediate feedback if their input is invalid or if the email is already registered, preventing submission of bad data.

**Why this priority**: Crucial for UX and data integrity to guide the user to provide the correct format.

**Independent Test**: Can be fully tested by triggering validation errors in the UI and observing inline error messages, or by attempting to register a duplicate email.

**Acceptance Scenarios**:

1. **Given** a user enters an invalid email format, **When** they attempt to submit or move focus, **Then** an inline error appears below the email field indicating the invalid format.
2. **Given** a user enters a weak password or non-matching passwords, **When** they attempt to submit, **Then** an inline error appears explaining the password requirements or mismatch.
3. **Given** a user enters an email that is already registered, **When** they submit, **Then** the server responds with 409 Conflict and an inline error is shown.
4. **Given** an unexpected server failure, **When** the user submits the form, **Then** a global alert "Error Interno del Servidor" is displayed.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST present a Sign Up form with fields: Nombre(s), Apellidos, Número telefónico, Correo electrónico, Contraseña, Confirmación de contraseña.
- **FR-002**: System MUST validate email format on the client side.
- **FR-003**: System MUST validate password strength (minimum characters and special characters per design) and password match on the client side.
- **FR-004**: System MUST display inline errors for specific field validations and a global alert for server errors, adhering to the Figma designs.
- **FR-005**: System MUST disable the submit button and show a loading spinner during form submission.
- **FR-006**: System MUST expose a POST `/api/v1/auth/signup` endpoint.
- **FR-007**: System MUST perform server-side validation and sanitization of all inputs.
- **FR-008**: System MUST securely hash user passwords using standard algorithms (e.g., bcrypt/argon2) before persistence.
- **FR-009**: System MUST prevent duplicate accounts by returning a 409 Conflict if the email already exists.
- **FR-010**: System MUST return a 201 Created on successful registration.
- **FR-011**: System MUST NOT return session tokens upon successful registration. The created user account MUST be stored in a "Pending" state, requiring admin approval before login is permitted.
- **FR-012**: System MUST use Tailwind CSS for all styling, matching the exact visual states (reposo, focus, error, carga, éxito) and responsive behavior from the Figma screenshots.

### Key Entities *(include if feature involves data)*

- **Usuario**: Represents a user of the system. Key attributes: ID, Nombre, Apellidos, Teléfono, Correo, Password Hash, Role, Status (e.g., Pending Approval, Active).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% of functional requirements and validations (client and server) pass automated tests.
- **SC-002**: No plain text passwords are ever stored or logged.
- **SC-003**: UI perfectly matches the Figma designs across all interaction states (focus, error, loading, success) and is responsive on mobile/desktop.
- **SC-004**: Endpoint response times for validation and creation are under 500ms under normal load.

## Assumptions

- Tailwind CSS is already configured in the project.
- Global alert components and input components can be built or reused if they exist.
- Assets from "assets/login" are available in the repository.
- The PostgreSQL database is used, consistent with the MediFlow golden rules.
- As per the UI success message "espera a que sea confirmada", the created user account is set to a "Pending" or inactive state initially.