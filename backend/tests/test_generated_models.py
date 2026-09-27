"""
Prueba unitaria para verificar los modelos Pydantic auto-generados desde OpenAPI 3.1.
US-01 — Definición del Contrato OpenAPI 3.1 y Generación de Tipos (SDD)

Ejecutar:
    python -m pytest tests/test_generated_models.py
"""

import pytest
from pydantic import ValidationError

from app._generated.models import (
    Clasificacion,
    DatosExtraidos,
    DecisionEnrutamiento,
    DiagnosticoEntidad,
    DocumentoClinico,
    EntidadesMedicas,
    ResultadoTriaje,
)


def test_instanciacion_resultado_triaje():
    """Verifica que ResultadoTriaje se cree correctamente con datos válidos."""
    triaje = ResultadoTriaje(
        status="procesado",
        documento_id="DOC-CLIN-2026-8942",
        clasificacion=Clasificacion(
            tipo_documento="Informe Clínico",
            especialidad="Cardiología",
            nivel_prioridad="Urgente",
            score_confianza_clasificacion=0.98,
        ),
        datos_extraidos=DatosExtraidos(
            diagnostico_principal="Angina de pecho",
            cie10_sugerido="I20.9",
        ),
        decision_enrutamiento=DecisionEnrutamiento(
            destino_principal="Cola_Emergencia_Medica",
            requiere_auditoria_humana=False,
            justificacion_enrutamiento="Gravedad alta asignada por riesgo coronario.",
        ),
    )

    assert triaje.model_dump()["clasificacion"]["nivel_prioridad"] == "Urgente"
    assert triaje.documento_id == "DOC-CLIN-2026-8942"
    assert triaje.clasificacion.score_confianza_clasificacion == 0.98


def test_entidades_medicas_ner():
    """Verifica la construcción del modelo EntidadesMedicas (NER clínico)."""
    entidades = EntidadesMedicas(
        diagnosticos=[
            DiagnosticoEntidad(texto="Angina de pecho (I20)", cie10="I20", es_principal=True)
        ],
        score_ner=0.95,
    )

    assert entidades.score_ner == 0.95
    assert entidades.diagnosticos is not None, "diagnosticos no debe ser None"
    assert len(entidades.diagnosticos) == 1
    assert entidades.diagnosticos[0].cie10 == "I20"


def test_validacion_score_ner_invalido():
    """Verifica que score_ner valide el rango 0.0 a 1.0."""
    with pytest.raises(ValidationError):
        EntidadesMedicas(
            score_ner=1.5  # ❌ Debe fallar porque excede 1.0
        )


def test_instanciacion_documento_clinico_request():
    """Verifica la construcción del modelo DocumentoClinico."""
    req = DocumentoClinico(
        documento_id="DOC-REQ-12345",
        tipo_archivo="PDF",
        documento_base64="SGVsbG8gTWVkaUZsb3c=",
        canal_origen="Guardia_Emergencias",
        metadata={"paciente_id": "PAC-12345"},
    )

    assert req.documento_id == "DOC-REQ-12345"
    assert req.tipo_archivo == "PDF"
    assert req.canal_origen == "Guardia_Emergencias"
    assert req.metadata is not None, "metadata no debe ser None"
    assert req.metadata["paciente_id"] == "PAC-12345"


def test_required_fields_and_optional_channel_match_current_api():
    with pytest.raises(ValidationError):
        DocumentoClinico(tipo_archivo="PDF")
    with pytest.raises(ValidationError):
        DocumentoClinico(documento_id="X")
    assert DocumentoClinico(documento_id="X", tipo_archivo="PDF").canal_origen == ""
    with pytest.raises(ValidationError):
        DocumentoClinico(documento_id="X", tipo_archivo="PDF", canal_origen=None)


def test_unknown_document_type_and_out_of_bounds_confidence_are_rejected():
    valid = dict(
        tipo_documento="Informe Clínico",
        nivel_prioridad="Rutina",
        score_confianza_clasificacion=0.8,
    )
    for change in [
        {"tipo_documento": "FACTURA"},
        {"score_confianza_clasificacion": -0.1},
        {"score_confianza_clasificacion": 1.1},
        {"nivel_prioridad": "INVENTADA"},
    ]:
        with pytest.raises(ValidationError):
            Clasificacion(**(valid | change))


def test_nullable_clinical_fields_round_trip():
    entities = EntidadesMedicas(diagnosticos=None, score_ner=None)
    assert EntidadesMedicas.model_validate_json(entities.model_dump_json()) == entities
    request = DocumentoClinico(documento_id="X", tipo_archivo="TEXTO", documento_texto=None)
    assert request.model_dump()["documento_texto"] is None
