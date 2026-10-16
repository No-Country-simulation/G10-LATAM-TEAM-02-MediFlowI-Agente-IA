"""La base de datos confirma el evento antes de que salga al SSE."""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app._generated.models import AlertaGuardia
from app.agent.nodes.routing import node_routing
from app.agent.state import AgentState
from app.core.alerts import MENSAJE_GUARDIA
from app.repositories.postgres_storage import DatabaseUnavailableError
from app.services.alert_service import AlertBroadcaster, AlertService


def alerta():
    return AlertaGuardia(
        id=uuid4(),
        documento_id="DOC-ALERTA",
        episodio_id=None,
        prioridad="Urgente",
        fecha=datetime.now(UTC),
        mensaje=MENSAJE_GUARDIA,
    )


async def test_persistir_antes_de_publicar_y_payload_minimo():
    broker = AlertBroadcaster()
    stored = alerta()

    async def persist(documento_id, usuario_id):
        assert queue.empty()
        assert (documento_id, usuario_id) == ("DOC-ALERTA", "usuario")
        return stored

    repository = Mock(registrar_alerta=AsyncMock(side_effect=persist))
    service = AlertService(repository=repository, broadcaster=broker)
    async with broker.subscribe() as queue:
        await service.emitir("DOC-ALERTA", "usuario")
        frame = await queue.get()
    assert frame.startswith(f"id: {stored.id}\nevent: ALERTA_GUARDIA_EMITIDA\ndata: ")
    payload = json.loads(frame.split("data: ", 1)[1])
    assert payload == stored.model_dump(mode="json")
    assert set(payload) == {"id", "documento_id", "episodio_id", "prioridad", "fecha", "mensaje"}
    assert frame.endswith("\n\n")


async def test_fallo_de_persistencia_no_emite():
    broker = AlertBroadcaster()
    repo = Mock(registrar_alerta=AsyncMock(side_effect=DatabaseUnavailableError("fallo")))
    async with broker.subscribe() as queue:
        with pytest.raises(DatabaseUnavailableError):
            await AlertService(repository=repo, broadcaster=broker).emitir("DOC", None)
        assert queue.empty()


async def test_routing_prepara_alerta_generica_sin_efectos_externos():
    state = AgentState(documento_id="DOC-ALERTA", tipo_archivo="TEXTO")
    state.clasificacion.nivel_prioridad = "Urgente"
    state.clasificacion.score_confianza_clasificacion = 0.9
    state.datos_extraidos.diagnostico_principal = "DIAGNOSTICO PRIVADO"
    result = await node_routing(state)
    notification = result["decision_enrutamiento"].notificacion_generada
    assert notification == {"canal": "Alerta_Guardia_Medica", "mensaje": MENSAJE_GUARDIA}


async def test_cie10_invalido_cancela_alerta_preparada():
    state = AgentState(documento_id="DOC", tipo_archivo="TEXTO")
    state.clasificacion.nivel_prioridad = "Urgente"
    state.metadata["cie10_codigos_invalidos"] = ["INVALIDO"]
    result = await node_routing(state)
    assert result["decision_enrutamiento"].notificacion_generada is None
