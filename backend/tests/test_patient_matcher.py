"""
Pruebas Unitarias para el Módulo de Resolución de Identidad y Conflictos DNI/HC.

Valida:
- US1: Cotejo de DNI y HC (asociado, sin_coincidencia, conflicto, resiliencia ante BD).
- US2: Enrutamiento forzado a Cola_Revision_Ambigua ante discrepancias.
- US3: Inyección de metadata y trazabilidad en el pipeline.
"""

from unittest.mock import AsyncMock, patch
import pytest

from app.agent.nodes.extraction import node_extraction
from app.agent.nodes.routing import _calcular_destino, node_routing
from app.agent.patient_matcher import (
    ResultadoMatchingPaciente,
    verificar_identidad_paciente,
)
from app.agent.state import (
    AgentState,
    ClasificacionState,
    DatosExtraidosState,
    PacienteState,
)
from app.repositories.postgres_storage import DatabaseUnavailableError


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def paciente_a():
    return {
        "id": "11111111-1111-1111-1111-111111111111",
        "numero_documento": "12345678",
        "historia_clinica": "HC-100",
        "nombres": "Carlos",
        "apellidos": "Mendoza",
    }


@pytest.fixture
def paciente_b():
    return {
        "id": "22222222-2222-2222-2222-222222222222",
        "numero_documento": "87654321",
        "historia_clinica": "HC-200",
        "nombres": "María",
        "apellidos": "López",
    }


# ── US1: Pruebas Unitarias de Matching (verificar_identidad_paciente) ──────────


@pytest.mark.asyncio
async def test_matching_sin_identificadores():
    """Si no se provee DNI ni HC, retorna sin_coincidencia sin error."""
    resultado = await verificar_identidad_paciente(None, None)
    assert resultado.estado == "sin_coincidencia"
    assert resultado.es_conflicto is False
    assert resultado.paciente is None


@pytest.mark.asyncio
async def test_matching_mismo_paciente(paciente_a):
    """Si DNI y HC corresponden al mismo paciente, retorna asociado."""
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "asociado", "paciente": paciente_a}),
    ):
        resultado = await verificar_identidad_paciente("12345678", "HC-100")
        assert resultado.estado == "asociado"
        assert resultado.es_conflicto is False
        assert resultado.paciente == paciente_a
        assert resultado.dni_evaluado == "12345678"
        assert resultado.hc_evaluada == "HC-100"


@pytest.mark.asyncio
async def test_matching_conflicto_pacientes_distintos():
    """Si DNI y HC corresponden a diferentes pacientes, retorna conflicto."""
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "conflicto", "paciente": None}),
    ):
        resultado = await verificar_identidad_paciente("12345678", "HC-200")
        assert resultado.estado == "conflicto"
        assert resultado.es_conflicto is True
        assert resultado.paciente is None
        assert "Discrepancia" in (resultado.motivo or "")
        assert resultado.dni_evaluado == "12345678"
        assert resultado.hc_evaluada == "HC-200"


@pytest.mark.asyncio
async def test_matching_solo_dni(paciente_a):
    """Si solo viene DNI y existe, retorna asociado."""
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "asociado", "paciente": paciente_a}),
    ):
        resultado = await verificar_identidad_paciente("12345678", None)
        assert resultado.estado == "asociado"
        assert resultado.es_conflicto is False
        assert resultado.paciente["id"] == paciente_a["id"]


@pytest.mark.asyncio
async def test_matching_solo_hc(paciente_a):
    """Si solo viene HC y existe, retorna asociado."""
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "asociado", "paciente": paciente_a}),
    ):
        resultado = await verificar_identidad_paciente(None, "HC-100")
        assert resultado.estado == "asociado"
        assert resultado.es_conflicto is False
        assert resultado.paciente["id"] == paciente_a["id"]


@pytest.mark.asyncio
async def test_matching_paciente_no_registrado():
    """Si los identificadores no existen en BD, retorna sin_coincidencia."""
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "sin_coincidencia", "paciente": None}),
    ):
        resultado = await verificar_identidad_paciente("99999999", "HC-999")
        assert resultado.estado == "sin_coincidencia"
        assert resultado.es_conflicto is False
        assert resultado.paciente is None


@pytest.mark.asyncio
async def test_matching_resiliencia_error_bd():
    """Si la base de datos no está disponible, captura DatabaseUnavailableError sin tumbar el servicio."""
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        side_effect=DatabaseUnavailableError("Conexión perdida"),
    ):
        resultado = await verificar_identidad_paciente("12345678", "HC-100")
        assert resultado.estado == "sin_coincidencia"
        assert resultado.es_conflicto is False
        assert "no disponible" in (resultado.motivo or "")


@pytest.mark.asyncio
async def test_matching_limpieza_espacios(paciente_a):
    """Limpia espacios en blanco antes de invocar el repositorio."""
    mock_resolver = AsyncMock(return_value={"estado": "asociado", "paciente": paciente_a})
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=mock_resolver,
    ):
        resultado = await verificar_identidad_paciente("  12345678  ", "  HC-100  ")
        assert resultado.estado == "asociado"
        mock_resolver.assert_called_once_with("12345678", "HC-100")


# ── US2: Pruebas de Enrutamiento a Cola_Revision_Ambigua (routing.py) ──────────


def test_calcular_destino_con_discrepancia_identidad():
    """Si existe discrepancia de identidad, se deriva a Cola_Revision_Ambigua con auditoría forzada."""
    destino, justificacion, notificacion, requiere_auditoria = _calcular_destino(
        score=0.95,
        nivel="Urgente",  # Aunque sea urgente, el conflicto de identidad tiene precedencia de seguridad
        diagnostico="TEP",
        paciente_nombre="Carlos",
        discrepancia_identidad=True,
    )

    assert destino == "Cola_Revision_Ambigua"
    assert requiere_auditoria is True
    assert notificacion is None
    assert "Discrepancia" in justificacion


@pytest.mark.asyncio
async def test_node_routing_interpola_flag_conflicto():
    """El nodo routing lee metadata.discrepancia_identidad_detectada y asigna status pendiente_auditoria."""
    state = AgentState(
        documento_id="DOC-CONFLICT-01",
        tipo_archivo="TEXTO",
        metadata={
            "discrepancia_identidad_detectada": True,
            "motivo_ambiguedad": "conflicto_identidad_dni_hc",
        },
        clasificacion=ClasificacionState(
            nivel_prioridad="Rutina",
            score_confianza_clasificacion=0.9,
        ),
    )

    result = await node_routing(state)

    assert result["decision_enrutamiento"].destino_principal == "Cola_Revision_Ambigua"
    assert result["decision_enrutamiento"].requiere_auditoria_humana is True
    assert result["status"] == "pendiente_auditoria"


@pytest.mark.asyncio
async def test_node_routing_estandar_sin_conflicto():
    """Sin flag de conflicto, el nodo routing opera con su lógica habitual."""
    state = AgentState(
        documento_id="DOC-NORMAL-01",
        tipo_archivo="TEXTO",
        metadata={},
        clasificacion=ClasificacionState(
            nivel_prioridad="Rutina",
            score_confianza_clasificacion=0.9,
        ),
    )

    result = await node_routing(state)

    assert result["decision_enrutamiento"].destino_principal == "Cola_Rutina"
    assert result["decision_enrutamiento"].requiere_auditoria_humana is False
    assert result["status"] == "procesado"


# ── US3: Integración en Nodo Extraction y Metadata ────────────────────────────


@pytest.mark.asyncio
async def test_extraction_node_integra_conflicto_identidad():
    """El nodo de extracción coteja identificadores y registra la metadata del conflicto."""
    json_llm = (
        '{"paciente": {"nombre": "Juan Pérez", "documento_identidad": "12345678", "historia_clinica": "HC-200"}, '
        '"diagnostico_principal": "Faringitis", "hallazgos_clave": []}'
    )
    mock_llm = AsyncMock()
    mock_llm.completar = AsyncMock(return_value=json_llm)

    state = AgentState(
        documento_id="DOC-EXTRACT-01",
        tipo_archivo="TEXTO",
        documento_texto="Paciente Juan Pérez con DNI 12345678 y HC HC-200",
    )

    # Mock del repositorio para que retorne conflicto
    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "conflicto", "paciente": None}),
    ):
        result = await node_extraction(state, llm_service=mock_llm)

        assert "datos_extraidos" in result
        assert result["metadata"]["discrepancia_identidad_detectada"] is True
        assert result["metadata"]["motivo_ambiguedad"] == "conflicto_identidad_dni_hc"
        assert result["metadata"]["dni_detectado"] == "12345678"
        assert result["metadata"]["hc_detectada"] == "HC-200"


@pytest.mark.asyncio
async def test_extraction_node_asocia_id_paciente(paciente_a):
    """El nodo de extracción asocia id_paciente si la resolución es exitosa."""
    json_llm = (
        '{"paciente": {"nombre": "Carlos Mendoza", "documento_identidad": "12345678", "historia_clinica": "HC-100"}, '
        '"diagnostico_principal": "Control", "hallazgos_clave": []}'
    )
    mock_llm = AsyncMock()
    mock_llm.completar = AsyncMock(return_value=json_llm)

    state = AgentState(
        documento_id="DOC-EXTRACT-02",
        tipo_archivo="TEXTO",
        documento_texto="Paciente Carlos Mendoza con DNI 12345678 y HC HC-100",
    )

    with patch(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        new=AsyncMock(return_value={"estado": "asociado", "paciente": paciente_a}),
    ):
        result = await node_extraction(state, llm_service=mock_llm)

        assert "datos_extraidos" in result
        assert result["datos_extraidos"].paciente.id_paciente == str(paciente_a["id"])
        # No debe haber flag de discrepancia
        assert result.get("metadata", {}).get("discrepancia_identidad_detectada") is not True
