"""Orquestación final: documentos, trazabilidad y publicación SSE en ese orden."""

from unittest.mock import AsyncMock, Mock

import pytest

from app.agent.state import AgentState, PacienteState
from app.repositories.oci_storage import StoragePersistenceError
from app.repositories.postgres_storage import DatabaseUnavailableError
from app.services.triage_service import TriageService


@pytest.fixture
def triage(monkeypatch, settings):
    state = AgentState(documento_id="DOC", tipo_archivo="TEXTO")
    state.clasificacion.nivel_prioridad = "Urgente"
    state.decision_enrutamiento.destino_principal = "Cola_Emergencia_Medica"
    graph = AsyncMock(return_value=state)
    monkeypatch.setattr("app.services.triage_service.ejecutar_triage", graph)
    db = Mock(guardar_resultado=AsyncMock(return_value=True))
    storage = Mock(guardar_documento=AsyncMock())
    alerts = Mock(emitir=AsyncMock())
    service = TriageService(settings, Mock(disponible=True), storage, db, alerts)
    return service, state, db, storage, alerts


async def test_documento_confirmado_antes_de_alertar(triage):
    service, state, db, storage, alerts = triage

    async def emit(doc, user):
        db.guardar_resultado.assert_awaited_once_with(state, "usuario")
        assert (doc, user) == ("DOC", "usuario")

    alerts.emitir.side_effect = emit
    assert await service.procesar_documento("DOC", "TEXTO", usuario_registro_id="usuario") is state
    alerts.emitir.assert_awaited_once()


@pytest.mark.parametrize("failure", [False, DatabaseUnavailableError("fallo")])
async def test_documento_no_confirmado_nunca_emite(triage, failure):
    service, _, db, _, alerts = triage
    if isinstance(failure, Exception):
        db.guardar_resultado.side_effect = failure
    else:
        db.guardar_resultado.return_value = failure
    with pytest.raises(DatabaseUnavailableError):
        await service.procesar_documento("DOC", "TEXTO")
    alerts.emitir.assert_not_awaited()


async def test_conflicto_posterior_al_grafo_cancela_alerta(triage, monkeypatch):
    service, state, _, _, alerts = triage
    state.datos_extraidos.paciente = PacienteState(documento_identidad="SINTETICO")
    state.decision_enrutamiento.notificacion_generada = {"mensaje": "preparada"}
    monkeypatch.setattr(
        "app.repositories.patient_repository.resolver_paciente_por_identificadores",
        AsyncMock(return_value={"estado": "conflicto"}),
    )
    await service.procesar_documento("DOC", "TEXTO")
    alerts.emitir.assert_not_awaited()
    assert state.decision_enrutamiento.notificacion_generada is None
    assert state.decision_enrutamiento.destino_principal == "Cola_Revision_Ambigua"


@pytest.mark.parametrize(
    "destino", ["Cola_Rutina", "Cola_Auditoria_Humana", "Farmacia_Hospitalaria"]
)
async def test_solo_emergencia_emite(triage, destino):
    service, state, _, _, alerts = triage
    state.decision_enrutamiento.destino_principal = destino
    await service.procesar_documento("DOC", "TEXTO")
    alerts.emitir.assert_not_awaited()


async def test_fallo_evento_propaga_error(triage):
    service, _, _, _, alerts = triage
    alerts.emitir.side_effect = DatabaseUnavailableError("evento no guardado")
    with pytest.raises(DatabaseUnavailableError):
        await service.procesar_documento("DOC", "TEXTO")


async def test_documento_confirmado_alerta_aunque_archivo_fisico_falle(triage):
    service, _, _, storage, alerts = triage
    storage.guardar_documento.side_effect = OSError("disco lleno")
    with pytest.raises(StoragePersistenceError):
        await service.procesar_documento("DOC", "TEXTO", documento_texto="sintético")
    alerts.emitir.assert_awaited_once()


def test_api_no_presenta_exito_si_falla_registro_alerta(client, bearer_headers, monkeypatch):
    monkeypatch.setattr(
        "app.repositories.alert_repository.AlertRepository.registrar_alerta",
        AsyncMock(side_effect=DatabaseUnavailableError("evento no persistido")),
    )
    response = client.post(
        "/api/v1/triage",
        headers=bearer_headers,
        json={
            "documento_id": "DOC-ALERTA-FALLO",
            "tipo_archivo": "TEXTO",
            "documento_texto": "TEP agudo detectado. Tromboembolismo pulmonar masivo. Correlación urgente.",
        },
    )
    assert response.status_code == 503
