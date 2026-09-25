from app.api.v1.patients import PatientCreateRequest


def test_patient_sex_is_optional_without_a_default_value():
    patient = PatientCreateRequest(
        numero_documento="12345678",
        nombres="Ana",
        apellidos="Pérez",
    )

    assert patient.sexo is None
