from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

from app.agent.state import AgentState
from app.core.config import get_settings
from app.repositories import oci_storage
from app.repositories.oci_storage import (
    OCIStorageRepository,
    StoragePersistenceError,
    StorageUnavailableError,
)


@pytest.mark.asyncio
async def test_local_mode_persists_to_the_selected_local_provider(tmp_path, monkeypatch):
    monkeypatch.setattr(oci_storage, "LOCAL_STORAGE_DIR", tmp_path)
    repository = OCIStorageRepository(get_settings(), storage_mode="LOCAL")

    saved = await repository.guardar_documento("procesados/DOC-1/resultado.json", "{}")

    assert saved is True
    assert (tmp_path / "procesados/DOC-1/resultado.json").read_text(encoding="utf-8") == "{}"


@pytest.mark.asyncio
async def test_local_write_failure_is_not_reported_as_success(tmp_path, monkeypatch):
    monkeypatch.setattr(oci_storage, "LOCAL_STORAGE_DIR", tmp_path)
    repository = OCIStorageRepository(get_settings(), storage_mode="LOCAL")

    def fail_write(*_args, **_kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", fail_write)

    with pytest.raises(StoragePersistenceError):
        await repository.guardar_documento("procesados/DOC-2/resultado.json", "{}")


@pytest.mark.asyncio
async def test_oci_mode_never_falls_back_to_local_without_credentials():
    settings = get_settings().model_copy(
        update={
            "oci_user_ocid": "",
            "oci_tenancy_ocid": "",
            "oci_namespace": "",
            "oci_fingerprint": "",
            "oci_private_key_path": "",
        }
    )
    repository = OCIStorageRepository(settings, storage_mode="OCI")

    with pytest.raises(StorageUnavailableError):
        await repository.guardar_documento("procesados/DOC-3/resultado.json", "{}")


@pytest.mark.asyncio
async def test_triage_reports_storage_failure_after_recording_it_in_postgres():
    from app.services.triage_service import TriageService

    result = AgentState(documento_id="DOC-STORAGE-FAIL", tipo_archivo="TEXTO")
    storage = AsyncMock()
    storage.guardar_documento.side_effect = StoragePersistenceError("disk full")
    postgres = AsyncMock()
    postgres.guardar_resultado.return_value = True
    service = TriageService(
        settings=get_settings(),
        llm_service=type("AvailableLLM", (), {"disponible": True})(),
        oci_storage=storage,
        postgres_storage=postgres,
    )

    with (
        patch(
            "app.services.triage_service.ejecutar_triage",
            new_callable=AsyncMock,
            return_value=result,
        ),
        pytest.raises(StoragePersistenceError),
    ):
        await service.procesar_documento(
            documento_id=result.documento_id,
            tipo_archivo="TEXTO",
            documento_texto="contenido clínico",
        )

    persisted_result = postgres.guardar_resultado.await_args.args[0]
    assert persisted_result.almacenamiento_oci.status_backup == "error"
