"""
MediFlow — Inyección de dependencias (DI).

Provee instancias singleton de clientes LLM y OCI para inyectar
en los endpoints y servicios via FastAPI Depends().
"""

from functools import lru_cache
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends

from app.core.config import Settings, get_settings

if TYPE_CHECKING:
    from app.repositories.oci_storage import OCIStorageRepository


# ── LLM Client ───────────────────────────────────────────────────────────────


@lru_cache
def get_llm_client(settings: Settings = Depends(get_settings)):
    """
    Retorna el cliente LLM configurado.
    Prioridad: Google Gemini → OpenAI (fallback).

    NOTA: El cliente real se inicializa en llm_service.py.
    Esta dependencia expone el settings para que el servicio lo use.
    """
    return settings


# ── OCI Storage Client ───────────────────────────────────────────────────────


def get_oci_storage(settings: Settings = Depends(get_settings)):
    """
    Retorna el cliente de OCI Object Storage.
    El proveedor efectivo se resuelve usando la selección manual de PostgreSQL.
    """
    from app.repositories.oci_storage import OCIStorageRepository

    return OCIStorageRepository(settings=settings)


# ── Type aliases para uso limpio en endpoints ─────────────────────────────────

SettingsDep = Annotated[Settings, Depends(get_settings)]
OCIStorageDep = Annotated["OCIStorageRepository", Depends(get_oci_storage)]
