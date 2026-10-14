"""Difusión independiente por cliente, sin bloquear el procesamiento clínico."""

import asyncio

import pytest

from app.services.alert_service import AlertBroadcaster


async def test_broadcast_a_todos_y_limpieza_al_desconectar():
    broadcaster = AlertBroadcaster()
    async with broadcaster.subscribe() as first, broadcaster.subscribe() as second:
        broadcaster.publish("evento confirmado")
        assert await asyncio.wait_for(first.get(), 1) == "evento confirmado"
        assert await asyncio.wait_for(second.get(), 1) == "evento confirmado"
        assert broadcaster.subscriber_count == 2
    assert broadcaster.subscriber_count == 0
    broadcaster.publish("sin clientes")


async def test_cliente_lento_se_cierra_sin_bloquear_otros():
    broadcaster = AlertBroadcaster(queue_size=1)
    async with broadcaster.subscribe() as slow, broadcaster.subscribe() as fast:
        broadcaster.publish("primero")
        assert await fast.get() == "primero"
        broadcaster.publish("segundo")
        assert await slow.get() is None
        assert await fast.get() == "segundo"
        assert broadcaster.subscriber_count == 1


async def test_cancelacion_libera_suscripcion():
    broadcaster = AlertBroadcaster()
    ready = asyncio.Event()

    async def listener():
        async with broadcaster.subscribe() as queue:
            ready.set()
            await queue.get()

    task = asyncio.create_task(listener())
    await ready.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert broadcaster.subscriber_count == 0


def test_cola_debe_ser_limitada():
    with pytest.raises(ValueError):
        AlertBroadcaster(queue_size=0)
