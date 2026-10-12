"""
Tests unitarios para la calibración del score de confianza multimodal (Issue #31).
Verifica:
1. Límites estrictos [0.0, 1.0] y redondeo a 3 decimales.
2. Ponderación por calidad de texto/OCR y completitud clínica (signos, diagnóstico, CIE-10).
3. Penalizaciones por degradación y errores previos.
4. Inyección de trazabilidad de factores en metadata con umbral HITL de 0.75.
"""

import pytest

from app.agent.nodes.confidence import (
    UMBRAL_CONFIANZA_HITL,
    calcular_score_confianza,
    node_confidence,
)
from app.agent.state import (
    AgentState,
    ClasificacionState,
    DatosExtraidosState,
    PacienteState,
)


def test_umbral_constante_es_0_75():
    """Verifica que el umbral de corte clínico HITL esté formalmente fijado en 0.75."""
    assert UMBRAL_CONFIANZA_HITL == 0.75


def test_calcular_score_limites_estrictos_0_a_1():
    """Garantiza que el score final nunca sea inferior a 0.0 ni superior a 1.0."""
    # Caso de desborde superior
    datos_completos = DatosExtraidosState(
        paciente=PacienteState(nombre="Juan Perez"),
        diagnostico_principal="Neumonía bacteriana aguda",
        cie10_sugerido="J15.9",
        hallazgos_clave=["Fiebre 39C", "Taquipnea", "SatO2 91%"],
    )
    score_alto, factores = calcular_score_confianza(
        score_base=0.95,
        datos=datos_completos,
        texto="Informe clínico detallado de paciente que presenta síntomas respiratorios de alta complejidad con datos completos...",
        error_mensaje=None,
    )
    assert 0.0 <= score_alto <= 1.0
    assert score_alto == 1.0

    # Caso de desborde inferior
    datos_vacios = DatosExtraidosState()
    score_bajo, factores_bajos = calcular_score_confianza(
        score_base=0.10,
        datos=datos_vacios,
        texto="doc corto",
        error_mensaje="Error previo de extracción OCR",
    )
    assert 0.0 <= score_bajo <= 1.0
    assert score_bajo == 0.0


def test_calcular_score_bonificaciones_completitud_clinica():
    """Verifica la suma adecuada de factores positivos de calidad y completitud."""
    datos = DatosExtraidosState(
        paciente=PacienteState(nombre="Maria Rodriguez"),
        diagnostico_principal="Hipertensión arterial esencial",
        cie10_sugerido="I10",
        hallazgos_clave=["PA 150/95 mmHg"],
    )
    texto_extenso = "Paciente femenino acude a control de hipertensión con sintomatología controlada. Se prescribe tratamiento y seguimiento continuo."
    
    score, factores = calcular_score_confianza(
        score_base=0.60,
        datos=datos,
        texto=texto_extenso,
        error_mensaje=None,
    )

    # Bonificaciones esperadas:
    # paciente (+0.10), diagnostico (+0.10), cie10 (+0.05), len(texto)>100 (+0.05), hallazgos (+0.05)
    # Total ajuste = +0.35 -> 0.60 + 0.35 = 0.95
    assert score == 0.95
    assert factores["score_base"] == 0.60
    assert factores["score_final"] == 0.95
    assert factores["retenido_por_confianza"] is False


def test_calcular_score_penalizaciones_texto_corto_y_error():
    """Verifica penalizaciones severas por texto insuficiente (< 20 chars), error y falta de diagnóstico."""
    datos_sin_diag = DatosExtraidosState(
        paciente=PacienteState(nombre="Anonimo"),
        diagnostico_principal=None,
    )
    texto_corto = "hola mundo"

    score, factores = calcular_score_confianza(
        score_base=0.70,
        datos=datos_sin_diag,
        texto=texto_corto,
        error_mensaje="Error de timeout OCR",
    )

    # Penalizaciones esperadas:
    # texto < 20 (-0.30), error (-0.20), sin diagnostico (-0.15)
    # paciente (+0.10)
    # Total ajuste = +0.10 - 0.60 = -0.50 -> 0.70 - 0.50 = 0.20
    assert round(score, 2) == 0.20
    assert factores["retenido_por_confianza"] is True
    assert factores["umbral_minimo_requerido"] == 0.75


@pytest.mark.asyncio
async def test_node_confidence_actualiza_estado_y_metadata():
    """Verifica que node_confidence actualice ClasificacionState y state.metadata con trazabilidad."""
    state = AgentState(
        documento_id="doc-conf-001",
        tipo_archivo="pdf",
        texto_extraido="Informe médico con contenido suficiente para análisis de triaje clínico de urgencia.",
        datos_extraidos=DatosExtraidosState(
            paciente=PacienteState(nombre="Carlos Gomez"),
            diagnostico_principal="Apendicitis aguda",
            cie10_sugerido="K35.8",
            hallazgos_clave=["Dolor en FID", "Fiebre"],
        ),
        clasificacion=ClasificacionState(
            tipo_documento="Informe_Medico",
            especialidad="Cirugia_General",
            nivel_prioridad="Urgente",
            score_confianza_clasificacion=0.55,
        ),
    )

    resultado = await node_confidence(state)

    assert "clasificacion" in resultado
    assert "metadata" in resultado
    assert "confidence" in resultado["nodos_ejecutados"]

    clasif = resultado["clasificacion"]
    # Score base 0.55 + 0.35 (paciente 0.10 + diag 0.10 + cie10 0.05 + hallazgos 0.05 + texto>100 0.0) = 0.85
    assert clasif.score_confianza_clasificacion >= 0.75
    
    metadata = resultado["metadata"]
    assert "factores_confianza" in metadata
    factores = metadata["factores_confianza"]
    assert factores["umbral_minimo_requerido"] == 0.75
    assert factores["score_final"] == clasif.score_confianza_clasificacion
    assert factores["retenido_por_confianza"] is False


@pytest.mark.asyncio
async def test_node_confidence_marca_retenido_si_score_menor_a_0_75():
    """Verifica que si el score calibrado resulta 0.74, se marque retenido_por_confianza=True."""
    state = AgentState(
        documento_id="doc-conf-bajo-002",
        tipo_archivo="pdf",
        texto_extraido="Texto corto",
        datos_extraidos=DatosExtraidosState(
            diagnostico_principal="Cefalea tensional",
        ),
        clasificacion=ClasificacionState(
            tipo_documento="Consulta",
            score_confianza_clasificacion=0.70,
        ),
    )

    resultado = await node_confidence(state)
    clasif = resultado["clasificacion"]
    factores = resultado["metadata"]["factores_confianza"]

    assert clasif.score_confianza_clasificacion < 0.75
    assert factores["retenido_por_confianza"] is True
