"""IA-09: un pase multimodal, aislamiento por solicitud y validaciones clínicas."""

import asyncio
import base64
import io
import json
from unittest.mock import AsyncMock, Mock

import pytest
from PIL import Image

from app.agent.graph import build_graph, ejecutar_triage
from app.core.config import Settings
from app.services.image_optimizer import MAX_BASE64_BYTES, optimizar_imagen
from app.services.llm_service import LLMService, LLMUnavailableError


def image_base64(mode="RGB", size=(400, 600)):
    with Image.new(mode, size, color=0) as image, io.BytesIO() as buffer:
        image.save(buffer, format="PNG")
        return base64.b64encode(buffer.getvalue()).decode()


def fusion_result(code="I219", priority="Urgente"):
    return json.dumps(
        {
            "texto_extraido": "Documento clínico sintético. Hallazgo consignado con indicación de revisión urgente. "
            * 2,
            "datos_extraidos": {
                "paciente": {"nombre": "PRUEBA IA09", "edad": 40},
                "diagnostico_principal": "Diagnóstico literal del documento",
                "cie10_sugerido": code,
                "hallazgos_clave": ["Hallazgo consignado"],
            },
            "clasificacion": {
                "tipo_documento": "Informe Clínico",
                "especialidad": None,
                "nivel_prioridad": priority,
                "razon_prioridad": "Prioridad consignada",
            },
        }
    )


async def run_image(llm, **kwargs):
    return await ejecutar_triage(
        documento_id="FUSION-PRUEBA",
        tipo_archivo="IMAGEN",
        documento_base64=image_base64(),
        llm_service=llm,
        **kwargs,
    )


def pdf_digital_base64(
    texto: str = "Hospital Central. Paciente refiere dolor torácico opresivo de 2 horas con diaforesis. Sospecha de infarto agudo de miocardio.",
) -> str:
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), texto)
    pdf_bytes = doc.tobytes()
    doc.close()
    return base64.b64encode(pdf_bytes).decode()


def pdf_escaneado_base64(header_text: str = "Receta") -> str:
    import fitz

    doc = fitz.open()
    page = doc.new_page()
    if header_text:
        page.insert_text((50, 72), header_text)
    with Image.new("RGB", (600, 800), color=(230, 230, 230)) as img, io.BytesIO() as buf:
        img.save(buf, format="PNG")
        page.insert_image(fitz.Rect(50, 100, 550, 750), stream=buf.getvalue())
    pdf_bytes = doc.tobytes()
    doc.close()
    return base64.b64encode(pdf_bytes).decode()


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "L", "P"])
def test_compresion_normaliza_formato_y_dimensiones(mode):
    original = image_base64(mode, (2000, 1500))
    optimized = optimizar_imagen(original)
    assert len(optimized.base64.encode()) < MAX_BASE64_BYTES
    with Image.open(io.BytesIO(base64.b64decode(optimized.base64))) as decoded:
        assert decoded.format == "JPEG"
        assert decoded.mode == "RGB"
        assert max(decoded.size) <= 1280


def test_compresion_adaptativa_mide_base64_no_solo_jpeg():
    with Image.effect_noise((3000, 2000), 100) as image, io.BytesIO() as buffer:
        image.save(buffer, format="PNG")
        optimized = optimizar_imagen(base64.b64encode(buffer.getvalue()).decode())
    assert len(optimized.base64.encode()) < 350_000
    assert optimized.ancho < 1280


@pytest.mark.parametrize("raw", ["no es base64", "", base64.b64encode(b"not an image").decode()])
def test_compresion_rechaza_entradas_invalidas(raw):
    with pytest.raises(ValueError):
        optimizar_imagen(raw)


async def test_un_viaje_y_reuso_sin_omitir_cie10_ni_cinco_nodos():
    llm = Mock(completar_imagen=AsyncMock(return_value=fusion_result()), completar=AsyncMock())
    result = await run_image(llm)
    llm.completar_imagen.assert_awaited_once()
    llm.completar.assert_not_awaited()
    assert result.datos_extraidos.cie10_sugerido == "I21.9"
    assert result.datos_extraidos.cie10_descripcion
    assert result.datos_extraidos.diagnostico_principal == "Diagnóstico literal del documento"
    assert result.decision_enrutamiento.destino_principal == "Cola_Emergencia_Medica"
    assert result.documento_base64 is None
    assert result.nodos_ejecutados == [
        "ingestion",
        "extraction",
        "classification",
        "confidence",
        "routing",
    ]


async def test_fusion_con_cie10_invalido_requiere_auditoria():
    llm = Mock(
        completar_imagen=AsyncMock(return_value=fusion_result("INVALIDO")), completar=AsyncMock()
    )
    result = await run_image(llm)
    assert result.datos_extraidos.cie10_sugerido is None
    assert result.metadata["cie10_codigos_invalidos"] == ["INVALIDO"]
    assert result.decision_enrutamiento.destino_principal == "Cola_Auditoria_Humana"
    assert result.decision_enrutamiento.notificacion_generada is None


@pytest.mark.parametrize(
    "raw", ["no JSON", "{}", "[]", '{"texto_extraido":" ","datos_extraidos":{},"clasificacion":{}}']
)
async def test_fusion_invalida_a_revision_sin_nuevas_llamadas(raw):
    llm = Mock(completar_imagen=AsyncMock(return_value=raw), completar=AsyncMock())
    result = await run_image(llm, documento_texto="Texto alternativo que no debe provocar llamadas")
    assert result.status == "pendiente_auditoria"
    assert result.decision_enrutamiento.destino_principal == "Cola_Auditoria_Humana"
    assert result.documento_base64 is None
    llm.completar_imagen.assert_awaited_once()
    llm.completar.assert_not_awaited()


async def test_error_vision_a_revision_y_limpieza():
    llm = Mock(completar_imagen=AsyncMock(side_effect=TimeoutError("fallo")), completar=AsyncMock())
    result = await run_image(llm)
    assert result.status == "pendiente_auditoria"
    assert result.documento_base64 is None
    llm.completar.assert_not_awaited()


async def test_imagen_danada_no_invoca_proveedor():
    llm = Mock(completar_imagen=AsyncMock(), completar=AsyncMock())
    result = await ejecutar_triage(
        "INVALIDA", "IMAGEN", documento_base64="invalida", llm_service=llm
    )
    assert result.status == "pendiente_auditoria"
    assert result.documento_base64 is None
    llm.completar_imagen.assert_not_awaited()
    llm.completar.assert_not_awaited()


async def test_conflicto_identidad_sigue_bloqueando_emergencia(monkeypatch):
    from app.agent.patient_matcher import ResultadoMatchingPaciente

    monkeypatch.setattr(
        "app.agent.patient_matcher.verificar_identidad_paciente",
        AsyncMock(
            return_value=ResultadoMatchingPaciente(estado="conflicto", es_conflicto=True),
        ),
    )
    llm = Mock(completar_imagen=AsyncMock(return_value=fusion_result()), completar=AsyncMock())
    result = await run_image(llm)
    assert result.decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"
    assert result.decision_enrutamiento.requiere_auditoria_humana


async def test_fusion_no_se_acepta_desde_metadata_del_cliente():
    llm = Mock(completar_imagen=AsyncMock(side_effect=RuntimeError()), completar=AsyncMock())
    result = await run_image(
        llm, metadata={"fusion_resultado": json.loads(fusion_result()), "fusion_exitosa": True}
    )
    assert result.status == "pendiente_auditoria"
    assert result.datos_extraidos.diagnostico_principal is None


async def test_grafo_singleton_aisla_solicitudes_concurrentes():
    assert build_graph() is build_graph()
    first = Mock(
        completar_imagen=AsyncMock(return_value=fusion_result("I219")), completar=AsyncMock()
    )
    second = Mock(
        completar_imagen=AsyncMock(return_value=fusion_result("J189")), completar=AsyncMock()
    )
    results = await asyncio.gather(run_image(first), run_image(second))
    assert [r.datos_extraidos.cie10_sugerido for r in results] == ["I21.9", "J18.9"]
    assert build_graph() is build_graph()


async def test_cliente_multimodal_construye_un_mensaje_con_jpeg():
    service = LLMService(
        Settings(
            google_api_key="your-test",
            openai_api_key="",
            allow_mock_llm=True,
            gemini_model="gemini-1.5-flash",
        )
    )
    service._provider = "gemini"
    service._client = Mock(ainvoke=AsyncMock(return_value=Mock(content=fusion_result())))
    result = await service.completar_imagen("prompt", "YWJj")
    assert result == fusion_result()
    service._client.ainvoke.assert_awaited_once()
    content = service._client.ainvoke.call_args.args[0][0].content
    assert content == [
        {"type": "text", "text": "prompt"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,YWJj"}},
    ]
    options = service._client.ainvoke.call_args.kwargs
    assert options["response_mime_type"] == "application/json"
    assert options["response_json_schema"]["properties"]["clasificacion"]
    assert "thinking_level" not in options  # El modelo legado no admite este parámetro.


async def test_fusion_gemini3_usa_low_sin_afectar_transcripcion_convencional():
    service = LLMService(
        Settings(google_api_key="", allow_mock_llm=True, gemini_model="gemini-3.5-flash-lite")
    )
    service._provider = "gemini"
    service._client = Mock(ainvoke=AsyncMock(return_value=Mock(content=fusion_result())))
    await service.completar_imagen("prompt", "YWJj")
    options = service._client.ainvoke.call_args.kwargs
    assert options["thinking_level"] == "low"
    assert options["include_thoughts"] is False
    assert "max_output_tokens" not in options  # No truncar transcripciones largas.
    await service.completar_multimodal("transcribe", ["YWJj"])
    assert service._client.ainvoke.call_args.kwargs == {}


def test_esquema_fusion_conserva_campos_y_no_duplica_anotaciones_en_prompt():
    from app.agent.fusion import esquema_fusion
    from app.agent.nodes.ingestion import _PROMPT_VISION_FUSION

    schema = esquema_fusion()
    assert "texto_extraido" in schema["required"]
    classification = schema["$defs"]["ClasificacionFusionVision"]
    assert "especialidad" in classification["required"]
    assert "medicamentos" in schema["$defs"]["DatosExtraidos"]["properties"]
    assert "title" not in schema
    assert "{esquema}" not in _PROMPT_VISION_FUSION


def test_cliente_gemini_configura_timeout_y_reintentos(monkeypatch):
    constructor = Mock()
    monkeypatch.setattr("langchain_google_genai.ChatGoogleGenerativeAI", constructor)
    LLMService(Settings(google_api_key="clave-sintetica-no-real", openai_api_key=""))
    assert constructor.call_args.kwargs["timeout"] == 30
    assert constructor.call_args.kwargs["max_retries"] == 2


async def test_fusion_no_cambia_a_openai_silenciosamente():
    service = LLMService(Settings(google_api_key="", openai_api_key="", allow_mock_llm=True))
    service._provider = "openai"
    service._client = Mock(ainvoke=AsyncMock())
    with pytest.raises(LLMUnavailableError):
        await service.completar_imagen("prompt", "YWJj")
    service._client.ainvoke.assert_not_awaited()


def test_webp_de_develop_se_comprime_como_jpeg():
    with Image.new("RGB", (900, 1200), "white") as image, io.BytesIO() as buffer:
        image.save(buffer, format="WEBP")
        optimized = optimizar_imagen(base64.b64encode(buffer.getvalue()).decode())
    with Image.open(io.BytesIO(base64.b64decode(optimized.base64))) as decoded:
        assert decoded.format == "JPEG"
    assert len(optimized.base64) < MAX_BASE64_BYTES


@pytest.mark.parametrize("medicamento,auditoria", [("Amoxicilina", False), ("Morfina", True)])
async def test_fusion_preserva_medicamentos_y_reglas_farmacia_de_develop(medicamento, auditoria):
    payload = json.loads(fusion_result("Z000", "Rutina"))
    payload["datos_extraidos"]["medicamentos"] = [
        {
            "medicamento": medicamento,
            "dosis": "Dosis consignada",
            "frecuencia": None,
            "via_administracion": None,
        }
    ]
    llm = Mock(completar_imagen=AsyncMock(return_value=json.dumps(payload)), completar=AsyncMock())
    result = await run_image(llm)
    assert result.datos_extraidos.medicamentos[0].medicamento == medicamento
    assert result.datos_extraidos.medicamentos[0].dosis == "Dosis consignada"
    assert result.decision_enrutamiento.destino_principal == "Farmacia_Hospitalaria"
    assert result.decision_enrutamiento.requiere_auditoria_humana is auditoria
    assert result.metodo_extraccion == "MULTIMODAL_VISION"
    llm.completar.assert_not_awaited()


async def test_fusion_fallida_no_reintenta_ocr_ni_llm(monkeypatch):
    ocr = Mock(side_effect=AssertionError("IA09 no debe ejecutar OCR de respaldo"))
    monkeypatch.setattr("app.agent.nodes.ingestion._extraer_texto_imagen_ocr", ocr)
    llm = Mock(completar_imagen=AsyncMock(side_effect=TimeoutError()), completar=AsyncMock())
    result = await run_image(llm)
    assert result.metodo_extraccion == "FALLBACK_AUDIT"
    assert result.status == "pendiente_auditoria"
    ocr.assert_not_called()
    llm.completar.assert_not_awaited()


def test_compresion_respeta_orientacion_exif_y_fondo_transparente():
    with Image.new("RGB", (800, 300), "white") as image, io.BytesIO() as buffer:
        exif = image.getexif()
        exif[274] = 6
        image.save(buffer, format="JPEG", exif=exif)
        optimized = optimizar_imagen(base64.b64encode(buffer.getvalue()).decode())
    assert (optimized.ancho, optimized.alto) == (300, 800)
    transparent = optimizar_imagen(image_base64("RGBA", (20, 20)))
    with Image.open(io.BytesIO(base64.b64decode(transparent.base64))) as decoded:
        assert decoded.getpixel((0, 0)) == (255, 255, 255)


async def test_transcripcion_larga_no_dispara_llamadas_por_bloques():
    payload = json.loads(fusion_result())
    payload["texto_extraido"] *= 100
    llm = Mock(completar_imagen=AsyncMock(return_value=json.dumps(payload)), completar=AsyncMock())
    result = await run_image(llm)
    assert len(result.texto_extraido) > 4000
    llm.completar_imagen.assert_awaited_once()
    llm.completar.assert_not_awaited()


async def test_especialidad_omitida_incumple_el_contrato_y_va_a_revision():
    payload = json.loads(fusion_result())
    del payload["clasificacion"]["especialidad"]
    llm = Mock(completar_imagen=AsyncMock(return_value=json.dumps(payload)), completar=AsyncMock())
    result = await run_image(llm)
    assert result.status == "pendiente_auditoria"
    llm.completar.assert_not_awaited()


def test_servicio_conserva_original_aunque_el_estado_libere_base64(
    client, bearer_headers, monkeypatch
):
    from app.repositories import oci_storage

    call = AsyncMock(return_value=fusion_result())
    monkeypatch.setattr(LLMService, "completar_imagen", call)
    original = image_base64()
    response = client.post(
        "/api/v1/triage",
        headers=bearer_headers,
        json={
            "documento_id": "FUSION-ORIGINAL",
            "tipo_archivo": "IMAGEN",
            "documento_base64": original,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["documento_base64"] is None
    assert response.json()["metadata"]["metodo_extraccion"] == "MULTIMODAL_VISION"
    assert (
        oci_storage.LOCAL_STORAGE_DIR / "recibidos/FUSION-ORIGINAL/original.png"
    ).read_bytes() == base64.b64decode(original)
    call.assert_awaited_once()


async def test_pdf_digital_suficiente_extrae_directamente_sin_vision():
    """US1: PDF digital con >= 50 caracteres clínicos útiles se extrae de inmediato sin visión."""
    llm = Mock(completar_imagen=AsyncMock(), completar_multimodal=AsyncMock(), completar=AsyncMock(return_value=json.dumps({"paciente": {"nombre": "TEST", "edad": 50}, "medico_solicitante": {"nombre": None, "matricula": None}, "estudio_realizado": None, "diagnostico_principal": "Dolor torácico", "cie10_sugerido": "I21.9", "hallazgos_clave": ["Dolor"], "medicamentos": []})))
    # Para classification mocked:
    llm.completar.side_effect = [
        json.dumps({"paciente": {"nombre": "TEST", "edad": 50}, "medico_solicitante": {"nombre": None, "matricula": None}, "estudio_realizado": None, "diagnostico_principal": "Dolor torácico", "cie10_sugerido": "I21.9", "hallazgos_clave": ["Dolor"], "medicamentos": []}),
        json.dumps({"tipo_documento": "Informe Clínico", "especialidad": "Cardiología", "nivel_prioridad": "Urgente", "razon_prioridad": "Dolor torácico agudo"}),
    ]

    result = await ejecutar_triage(
        documento_id="PDF-DIGITAL-01",
        tipo_archivo="PDF",
        documento_base64=pdf_digital_base64(),
        llm_service=llm,
    )

    # Verifica que NO se llamó a modelos de visión
    llm.completar_imagen.assert_not_called()
    llm.completar_multimodal.assert_not_called()
    assert result.metodo_extraccion == "TEXT_EXTRACTION"
    assert "dolor torácico" in result.texto_extraido.lower()
    assert result.documento_base64 is None
    assert result.status == "procesado"


async def test_pdf_escaneado_insuficiente_activa_pipeline_fusion_un_solo_pase():
    """US2: PDF escaneado con < 50 caracteres activa Pipeline Fusion rasterizando en memoria."""
    llm = Mock(completar_imagen=AsyncMock(return_value=fusion_result("I219", "Urgente")), completar=AsyncMock())

    result = await ejecutar_triage(
        documento_id="PDF-SCAN-01",
        tipo_archivo="PDF",
        documento_base64=pdf_escaneado_base64("Receta"),
        llm_service=llm,
    )

    # Verifica pase único de Gemini Vision
    llm.completar_imagen.assert_awaited_once()
    llm.completar.assert_not_awaited()
    assert result.metodo_extraccion == "MULTIMODAL_VISION"
    assert result.datos_extraidos.cie10_sugerido == "I21.9"
    assert result.decision_enrutamiento.destino_principal == "Cola_Emergencia_Medica"
    assert result.documento_base64 is None
    assert result.status == "procesado"


async def test_pdf_corrupto_deriva_a_fallback_audit_y_libera_memoria():
    """US3: PDF corrupto libera documento_base64 y deriva a FALLBACK_AUDIT de forma segura."""
    llm = Mock(completar_imagen=AsyncMock(), completar=AsyncMock())
    corrupted_pdf = base64.b64encode(b"%PDF-1.4 corrupt content not valid").decode()

    result = await ejecutar_triage(
        documento_id="PDF-CORRUPT-01",
        tipo_archivo="PDF",
        documento_base64=corrupted_pdf,
        llm_service=llm,
    )

    assert result.metodo_extraccion == "FALLBACK_AUDIT"
    assert result.status == "pendiente_auditoria"
    assert result.documento_base64 is None
    llm.completar_imagen.assert_not_called()


async def test_pdf_escaneado_multipagina_concatena_en_memoria_y_optimiza():
    """US2: PDF multipágina escaneado (hasta 3 páginas) se concatena en memoria y optimiza a < 350 KB."""
    import fitz
    doc = fitz.open()
    for i in range(2):
        page = doc.new_page()
        with Image.new("RGB", (500, 700), color=(240, 240, 240)) as img, io.BytesIO() as buf:
            img.save(buf, format="PNG")
            page.insert_image(fitz.Rect(50, 50, 450, 650), stream=buf.getvalue())
    pdf_bytes = doc.tobytes()
    doc.close()
    multipage_b64 = base64.b64encode(pdf_bytes).decode()

    llm = Mock(completar_imagen=AsyncMock(return_value=fusion_result("J459", "Urgente")), completar=AsyncMock())
    result = await ejecutar_triage(
        documento_id="PDF-SCAN-MULTI",
        tipo_archivo="PDF",
        documento_base64=multipage_b64,
        llm_service=llm,
    )

    llm.completar_imagen.assert_awaited_once()
    assert result.metodo_extraccion == "MULTIMODAL_VISION"
    assert result.documento_base64 is None
    assert result.status == "procesado"


async def test_pdf_escaneado_fallo_vision_deriva_a_fallback_audit():
    """US3: Ante error en llamada de visión en PDF escaneado, deriva directamente a FALLBACK_AUDIT sin reintentos costosos."""
    llm = Mock(completar_imagen=AsyncMock(side_effect=TimeoutError("Timeout Gemini Vision")), completar=AsyncMock())
    result = await ejecutar_triage(
        documento_id="PDF-SCAN-TIMEOUT",
        tipo_archivo="PDF",
        documento_base64=pdf_escaneado_base64("Receta"),
        llm_service=llm,
    )

    llm.completar_imagen.assert_awaited_once()
    llm.completar.assert_not_awaited()
    assert result.metodo_extraccion == "FALLBACK_AUDIT"
    assert result.status == "pendiente_auditoria"
    assert result.documento_base64 is None
