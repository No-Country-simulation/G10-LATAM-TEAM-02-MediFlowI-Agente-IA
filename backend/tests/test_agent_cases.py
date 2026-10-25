import base64
import io
import sys
from types import SimpleNamespace

import pytest
from PIL import Image

from app.agent.graph import ejecutar_triage
from app.agent.nodes import ingestion
from app.agent.nodes.classification import consolidar_clasificaciones
from app.agent.nodes.extraction import _parsear_respuesta, dividir_texto_en_bloques
from app.agent.nodes.routing import _calcular_destino
from app.agent.state import ClasificacionState
from app.core.config import get_settings
from app.services.llm_service import LLMService, LLMUnavailableError


def test_dividir_texto_en_bloques_preserva_el_final_del_documento():
    texto = "a" * 4_000 + "HALLAZGO_FINAL_CRITICO"

    bloques = dividir_texto_en_bloques(texto, max_chars=4_000)

    assert bloques == ["a" * 4_000, "HALLAZGO_FINAL_CRITICO"]


@pytest.mark.asyncio
async def test_llm_sin_credenciales_no_genera_resultados_clinicos_ficticios():
    settings = get_settings().model_copy(
        update={
            "google_api_key": "",
            "openai_api_key": "",
            "allow_mock_llm": False,
        }
    )
    llm = LLMService(settings=settings)

    assert llm.proveedor == "unavailable"
    assert llm.disponible is False
    with pytest.raises(LLMUnavailableError):
        await llm.completar("Clasifica este documento clínico")


def test_pdf_sin_capa_texto_usa_fallback_ocr(monkeypatch):
    monkeypatch.setattr(ingestion, "_extraer_texto_pdf_pymupdf", lambda _: "")
    monkeypatch.setattr(ingestion, "_extraer_texto_pdf_ocr", lambda _: "texto OCR")

    assert ingestion._extraer_texto_pdf("cGRm") == "texto OCR"


def test_imagen_ejecuta_ocr_tesseract_en_espanol(monkeypatch):
    image_buffer = io.BytesIO()
    Image.new("RGB", (2, 2), color="white").save(image_buffer, format="PNG")
    monkeypatch.setitem(
        sys.modules,
        "pytesseract",
        SimpleNamespace(image_to_string=lambda image, lang: "Receta médica"),
    )

    texto = ingestion._extraer_texto_imagen(base64.b64encode(image_buffer.getvalue()).decode())

    assert texto == "Receta médica"


def test_prioridad_ambigua_usa_cola_operativa_dedicada():
    destino, _, _, requiere_auditoria = _calcular_destino(
        score=0.8,
        nivel="Ambiguo",
        diagnostico=None,
        paciente_nombre=None,
    )

    assert destino == "Cola_Revision_Ambigua"
    assert requiere_auditoria is True


def test_consolidar_clasificaciones_prioriza_urgente_en_bloque_final():
    clasificacion = consolidar_clasificaciones(
        [
            ClasificacionState(
                tipo_documento="Evolución Clínica",
                nivel_prioridad="Rutina",
                score_confianza_clasificacion=0.8,
            ),
            ClasificacionState(
                tipo_documento="Informe de Estudio por Imagenes",
                nivel_prioridad="Urgente",
                score_confianza_clasificacion=0.85,
            ),
        ]
    )

    assert clasificacion.nivel_prioridad == "Urgente"
    assert clasificacion.tipo_documento == "Informe de Estudio por Imagenes"


def test_extraccion_conserva_dni_e_historia_clinica():
    datos = _parsear_respuesta(
        '{"paciente": {"nombre": "Ana", "documento_identidad": "12345678", "historia_clinica": "HC-01"}}'
    )

    assert datos.paciente.documento_identidad == "12345678"
    assert datos.paciente.historia_clinica == "HC-01"


@pytest.mark.asyncio
async def test_caso_1_rutina():
    """
    Caso 1 (Rutina): Documento clínico de analítica normal.
    Debe enrutarse a Cola_Rutina con score_confianza >= 0.8.
    """
    settings = get_settings()
    llm = LLMService(settings=settings)

    resultado = await ejecutar_triage(
        documento_id="DOC-001",
        tipo_archivo="TEXTO",
        documento_texto="Analítica normal. Hemograma completo sin hallazgos patológicos.",
        canal_origen="Consulta_Externa",
        llm_service=llm,
    )

    assert resultado.status == "procesado"
    assert resultado.decision_enrutamiento.destino_principal == "Cola_Rutina"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is False
    assert resultado.clasificacion.score_confianza_clasificacion >= 0.75
    assert "ingestion" in resultado.nodos_ejecutados
    assert "extraction" in resultado.nodos_ejecutados
    assert "classification" in resultado.nodos_ejecutados
    assert "confidence" in resultado.nodos_ejecutados
    assert "routing" in resultado.nodos_ejecutados


@pytest.mark.asyncio
async def test_caso_2_urgencia_tep():
    """
    Caso 2 (Urgencia): Informe radiológico crítico con TEP agudo.
    Debe enrutarse a Cola_Emergencia_Medica y generar notificación/alerta.
    """
    settings = get_settings()
    llm = LLMService(settings=settings)

    resultado = await ejecutar_triage(
        documento_id="DOC-002",
        tipo_archivo="TEXTO",
        documento_texto="HOSPITAL SANTA LUCIA. Tomografía de Tórax. Hallazgo: Defecto de llenado en arteria pulmonar compatible con TEP agudo. Se requiere correlación clínica urgente.",
        canal_origen="Guardia_Emergencias",
        llm_service=llm,
    )

    assert resultado.status == "procesado"
    assert resultado.decision_enrutamiento.destino_principal == "Cola_Emergencia_Medica"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is False
    assert resultado.clasificacion.nivel_prioridad == "Urgente"
    assert resultado.decision_enrutamiento.notificacion_generada is not None
    assert "Alerta" in resultado.decision_enrutamiento.notificacion_generada.get("canal", "")


@pytest.mark.asyncio
async def test_caso_3_ambiguo_hitl():
    """
    Caso 3 (Ambiguo): Documento con texto ilegible o baja legibilidad.
    Debe derivarse a Cola_Revision_Ambigua con requiere_auditoria_humana = True.
    """
    settings = get_settings()
    llm = LLMService(settings=settings)

    resultado = await ejecutar_triage(
        documento_id="DOC-003",
        tipo_archivo="TEXTO",
        documento_texto="... texto ilegible ... px ... 45 ... mgr ??? firma no visible",
        canal_origen="Admision",
        llm_service=llm,
    )

    assert resultado.decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is True
    assert resultado.status == "pendiente_auditoria"


@pytest.mark.asyncio
async def test_caso_4_conflicto_identidad_dni_hc():
    """
    Caso 4 (Conflicto DNI/HC): Documento con DNI y HC cruzados de distintos pacientes.
    Debe derivarse forzosamente a Cola_Revision_Ambigua con requiere_auditoria_humana = True
    y registrar la discrepancia en metadata.
    """
    from unittest.mock import AsyncMock, patch

    settings = get_settings()
    llm = LLMService(settings=settings)

    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "conflicto", "paciente": None}),
    ):
        resultado = await ejecutar_triage(
            documento_id="DOC-004-CONFLICT",
            tipo_archivo="TEXTO",
            documento_texto="HOSPITAL SANTA LUCIA. Paciente Carlos con DNI 12345678 y HC HC-999. Control de rutina sin hallazgos.",
            canal_origen="Consulta_Externa",
            llm_service=llm,
        )

    assert resultado.decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"
    assert resultado.decision_enrutamiento.requiere_auditoria_humana is True
    assert resultado.status == "pendiente_auditoria"
    assert resultado.metadata.get("discrepancia_identidad_detectada") is True
    assert resultado.metadata.get("motivo_ambiguedad") == "conflicto_identidad_dni_hc"


def test_parsear_respuesta_extraccion_defensiva():
    """Valida que _parsear_respuesta en extraction tolere listas y bloques Markdown con espacios."""
    from app.agent.nodes.extraction import _parsear_respuesta

    payload_lista = [
        {"type": "text", "text": "```json\n{\n  \"paciente\": {\"nombre\": \"Mateo Torres\"},\n"},
        {"type": "text", "text": "  \"diagnostico_principal\": \"Amigdalitis aguda\",\n  \"cie10_sugerido\": \"J03.9\"\n}\n```"},
    ]
    datos = _parsear_respuesta(payload_lista)
    assert datos.paciente is not None
    assert datos.paciente.nombre == "Mateo Torres"
    assert datos.diagnostico_principal == "Amigdalitis aguda"
    assert datos.cie10_sugerido == "J03.9"

    # Entrada no válida o vacía retorna estado seguro
    assert _parsear_respuesta(None).diagnostico_principal is None
    assert _parsear_respuesta("texto no json").diagnostico_principal is None


def test_parsear_respuesta_clasificacion_defensiva():
    """Valida que _parsear_respuesta en classification tolere listas y bloques Markdown."""
    from app.agent.nodes.classification import _parsear_respuesta

    payload_lista = [
        {"type": "text", "text": "```json\n{\n  \"tipo_documento\": \"Informe Clínico\",\n"},
        {"type": "text", "text": "  \"nivel_prioridad\": \"Urgente\",\n  \"especialidad\": \"Medicina General\"\n}\n```"},
    ]
    clasif = _parsear_respuesta(payload_lista)
    assert clasif.tipo_documento == "Informe Clínico"
    assert clasif.nivel_prioridad == "Urgente"
    assert clasif.especialidad == "Medicina General"
    assert clasif.score_confianza_clasificacion == 0.85

    # Entrada vacía o inválida retorna estado ambiguo seguro
    vacio = _parsear_respuesta("")
    assert vacio.nivel_prioridad == "Ambiguo"
    assert vacio.tipo_documento == "Otro"


@pytest.mark.asyncio
async def test_ejecutar_triage_con_llm_multimodal_lista():
    """Verifica que el pipeline de triaje complete exitosamente con LLM devolviendo bloques multiformato."""
    from unittest.mock import AsyncMock, MagicMock

    from langchain_core.messages import AIMessage

    settings = get_settings()
    llm = LLMService(settings=settings)
    mock_client = MagicMock()
    
    extraction_json = '```json\n{"paciente": {"nombre": "Juan Pérez", "documento_identidad": "12345678"}, "diagnostico_principal": "Faringoamigdalitis", "cie10_sugerido": "J03.9", "hallazgos_clave": ["Fiebre"]}\n```'
    classification_json = '```json\n{"tipo_documento": "Informe Clínico", "especialidad": "Medicina General", "nivel_prioridad": "Rutina"}\n```'

    async def mock_ainvoke(messages):
        content = messages[0].content
        if "extrae" in content.lower() or "diagnostico_principal" in content.lower():
            return AIMessage(content=[{"type": "text", "text": extraction_json}])
        return AIMessage(content=[{"type": "text", "text": classification_json}])

    mock_client.ainvoke = AsyncMock(side_effect=mock_ainvoke)
    llm._client = mock_client
    llm._provider = "gemini"

    resultado = await ejecutar_triage(
        documento_id="DOC-MULTIMODAL-01",
        tipo_archivo="TEXTO",
        documento_texto="Paciente Juan Pérez con DNI 12345678. Presenta dolor de garganta y fiebre.",
        canal_origen="Consulta_Externa",
        llm_service=llm,
    )

    assert resultado.status == "procesado"
    assert resultado.datos_extraidos.paciente.nombre == "Juan Pérez"
    assert resultado.datos_extraidos.diagnostico_principal == "Faringoamigdalitis"
    assert resultado.datos_extraidos.cie10_sugerido == "J03.9"
    assert resultado.clasificacion.nivel_prioridad == "Rutina"
    assert resultado.clasificacion.score_confianza_clasificacion >= 0.80
    assert not resultado.error_mensaje


def test_parsear_respuesta_extrae_medicamentos_prescritos():
    """T005 [US1] Verifica que _parsear_respuesta deserialice correctamente la lista de medicamentos."""
    from app.agent.nodes.extraction import _parsear_respuesta

    payload_json = """{
        "paciente": {"nombre": "Juan Pérez", "edad": 45},
        "diagnostico_principal": "Faringoamigdalitis aguda",
        "cie10_sugerido": "J03.9",
        "medicamentos": [
            {
                "medicamento": "Amoxicilina",
                "dosis": "500 mg",
                "frecuencia": "cada 8 horas",
                "via_administracion": "oral"
            },
            {
                "medicamento": "Paracetamol",
                "dosis": "500 mg",
                "frecuencia": "cada 8 horas",
                "via_administracion": "oral"
            }
        ]
    }"""

    datos = _parsear_respuesta(payload_json)
    assert len(datos.medicamentos) == 2
    assert datos.medicamentos[0].medicamento == "Amoxicilina"
    assert datos.medicamentos[0].dosis == "500 mg"
    assert datos.medicamentos[0].frecuencia == "cada 8 horas"
    assert datos.medicamentos[0].via_administracion == "oral"
    assert datos.medicamentos[1].medicamento == "Paracetamol"


def test_consolidar_datos_combina_medicamentos_sin_duplicados():
    """T010 [US2] Verifica que _consolidar_datos combine listas de medicamentos eliminando duplicados exactos."""
    from app.agent.nodes.extraction import _consolidar_datos
    from app.agent.state import DatosExtraidosState, MedicamentoPrescritoState

    acumulado = DatosExtraidosState(
        medicamentos=[
            MedicamentoPrescritoState(
                medicamento="Amoxicilina",
                dosis="500 mg",
                frecuencia="cada 8 horas",
                via_administracion="oral",
            ),
            MedicamentoPrescritoState(
                medicamento="Ibuprofeno",
                dosis="400 mg",
                frecuencia="cada 8 horas",
                via_administracion="oral",
            ),
        ]
    )

    nuevo = DatosExtraidosState(
        medicamentos=[
            MedicamentoPrescritoState(
                medicamento="amoxicilina",  # Duplicado con distinta capitalización
                dosis="500 mg",
                frecuencia="cada 8 horas",
                via_administracion="oral",
            ),
            MedicamentoPrescritoState(
                medicamento="Omeprazol",  # Fármaco nuevo
                dosis="20 mg",
                frecuencia="cada 24 horas",
                via_administracion="oral",
            ),
        ]
    )

    consolidado = _consolidar_datos(acumulado, nuevo)
    assert len(consolidado.medicamentos) == 3
    nombres = [m.medicamento for m in consolidado.medicamentos]
    assert nombres == ["Amoxicilina", "Ibuprofeno", "Omeprazol"]


def test_medicamentos_tolerancia_valores_parciales_y_nulos():
    """T011 [US2] Verifica que se capturen medicamentos cuando faltan dosis, frecuencia o vía."""
    from app.agent.nodes.extraction import _parsear_respuesta

    payload_json = """{
        "medicamentos": [
            {
                "medicamento": "Aspirina",
                "dosis": null,
                "frecuencia": null,
                "via_administracion": null
            },
            {
                "medicamento": "Metformina 850mg",
                "dosis": "850 mg"
            },
            {
                "medicamento": "   ",
                "dosis": "100 mg"
            },
            {
                "otra_clave": "no es medicamento"
            }
        ]
    }"""

    datos = _parsear_respuesta(payload_json)
    # Debe filtrar los inválidos (sin nombre o con espacios) y conservar los dos válidos
    assert len(datos.medicamentos) == 2
    assert datos.medicamentos[0].medicamento == "Aspirina"
    assert datos.medicamentos[0].dosis is None
    assert datos.medicamentos[0].frecuencia is None
    assert datos.medicamentos[0].via_administracion is None
    assert datos.medicamentos[1].medicamento == "Metformina 850mg"
    assert datos.medicamentos[1].dosis == "850 mg"


def test_documento_sin_medicamentos_retorna_lista_vacia():
    """T014 [US3] Verifica que documentos sin prescripciones inicialicen medicamentos como lista vacía."""
    from app.agent.nodes.extraction import _parsear_respuesta

    payload_json = """{
        "estudio_realizado": "Radiografía de Tórax",
        "diagnostico_principal": "Campos pulmonares normales",
        "hallazgos_clave": ["Sin condensaciones"]
    }"""

    datos = _parsear_respuesta(payload_json)
    assert datos.medicamentos == []
    assert isinstance(datos.medicamentos, list)


