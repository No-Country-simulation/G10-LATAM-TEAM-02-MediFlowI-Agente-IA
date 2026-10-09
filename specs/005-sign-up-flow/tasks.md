# Tasks: Sign Up Flow

**Input**: Design documents from `/specs/005-sign-up-flow/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md

**Tests**: Included and MANDATORY due to the "Zero Regressions" Constitution rule (100% coverage).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Exact file paths are included.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Add `bcrypt` dependency to `backend/requirements.txt`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Setup database schema migration for `users` table in `backend/alembic/versions/` (based on data-model.md)
- [x] T003 Create/Update SQLAlchemy model `User` in `backend/app/models/user.py`
- [x] T004 [P] Implement password hashing utilities using `bcrypt` in `backend/app/core/security.py`
- [x] T005 [P] Create Pydantic schemas for user signup in `backend/app/schemas/user.py`

**Checkpoint**: Foundation ready - database and core utilities exist.

---

## Phase 3: User Story 1 - Successful Registration Request (Priority: P1) 🎯 MVP

**Goal**: Users can request a new account by providing info and password, receiving visual confirmation.

**Independent Test**: API endpoint returns 201 Created and saves user in 'PENDING' state. UI submits form successfully.

### Tests for User Story 1 ⚠️ (MANDATORY)

- [x] T006 [P] [US1] Create unit tests for password hashing in `backend/tests/core/test_security.py`
- [x] T007 [P] [US1] Create API endpoint tests for successful signup in `backend/tests/api/v1/test_auth.py`
- [x] T008 [P] [US1] Create React component tests for SignUpForm (success path) in `frontend/src/tests/components/auth/SignUpForm.test.tsx`

### Implementation for User Story 1

- [x] T009 [US1] Implement POST `/api/auth/signup` endpoint in `backend/app/api/v1/auth.py` (depends on T003, T004, T005)
- [x] T010 [P] [US1] Create API client `signup` function in `frontend/src/services/auth.api.ts`
- [x] T011 [US1] Implement `SignUpForm` component (UI structure, Tailwind CSS, loading spinner, & success logic) in `frontend/src/components/auth/SignUpForm.tsx` (depends on T010)
- [x] T012 [P] [US1] Implement `SignUpPage` to host the form in `frontend/src/pages/SignUpPage.tsx`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently (happy path).

---

## Phase 4: User Story 2 - Validation and Error Handling (Priority: P1)

**Goal**: Users receive clear feedback on invalid input or duplicate email.

**Independent Test**: API rejects duplicate emails with 409. Form displays inline errors for email/password mismatches.

### Tests for User Story 2 ⚠️ (MANDATORY)

- [x] T013 [P] [US2] Update API endpoint tests for duplicate email and weak password validations in `backend/tests/api/v1/test_auth.py`
- [x] T014 [P] [US2] Update React component tests for validation errors in `frontend/src/tests/components/auth/SignUpForm.test.tsx`

### Implementation for User Story 2

- [x] T015 [US2] Update backend endpoint to handle unique constraint violation for duplicate emails (return 409) in `backend/app/api/v1/auth.py`
- [x] T016 [US2] Update Pydantic schemas with strong validation rules (email format, strong password) in `backend/app/schemas/user.py`
- [x] T017 [US2] Update `SignUpForm.tsx` to handle client-side validations (email format, password match) and display inline errors in `frontend/src/components/auth/SignUpForm.tsx`
- [x] T018 [US2] Update `SignUpForm.tsx` to catch backend 400/409 errors for inline display, and global 500 alerts in `frontend/src/components/auth/SignUpForm.tsx`

**Checkpoint**: Validation and duplicate handling fully working.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Final verifications and cleanup.

- [x] T019 Run `quickstart.md` validation.
- [x] T020 Run backend & frontend test suites to ensure 100% green builds (`pytest` & `vitest`).

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD).
- Models before services.
- Endpoints before UI integration.
- Story complete before moving to next phase.

### Parallel Opportunities

- Pydantic Schemas (T005) and Password hashing (T004) can run in parallel.
- All tests for a user story marked [P] can run in parallel (T006, T007, T008).
- UI component structure and API implementation can run concurrently once API contract is agreed upon.

---

## Implementation Strategy

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready.
2. Add User Story 1 → Test independently → Happy path works.
3. Add User Story 2 → Test independently → Edge cases and validations handled.
4. Final validation with Quickstart.

