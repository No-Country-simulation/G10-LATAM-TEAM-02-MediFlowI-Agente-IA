"""
MediFlow — Repositorio OCI Object Storage.

Maneja la persistencia de documentos procesados en OCI Object Storage
usando la capa Always Free del Hackathon ONE G10.

Buckets:
  procesados/urgentes/    → documentos urgentes (TEP, emergencias)
  procesados/rutina/      → documentos de rutina
  auditoria_humana/       → pendientes de revisión HITL
"""

import io
from pathlib import Path

import structlog

from app.core.config import Settings

logger = structlog.get_logger(__name__)

LOCAL_STORAGE_DIR = Path(__file__).resolve().parent.parent.parent / "storage"


class StorageUnavailableError(RuntimeError):
    """El proveedor de archivos seleccionado no está disponible."""


class StoragePersistenceError(RuntimeError):
    """El proveedor no pudo persistir el archivo solicitado."""


class OCIStorageRepository:
    """
    Repositorio para OCI Object Storage.

    En modo desarrollo (sin credenciales OCI configuradas),
    guarda automáticamente los archivos en el disco local (backend/storage/).
    """

    _shared_mock_store: dict[str, str] = {}

    def __init__(self, settings: Settings, storage_mode: str | None = None):
        self._settings = settings
        self._storage_mode = storage_mode.upper() if storage_mode else None
        self._client = None
        self._mock_store = self._shared_mock_store
        self._initialized = False

    async def _inicializar(self) -> None:
        """Inicializa exclusivamente el proveedor elegido manualmente en PostgreSQL."""
        if self._initialized:
            return

        if self._storage_mode is None:
            from app.repositories.postgres_storage import get_storage_mode

            self._storage_mode = await get_storage_mode()

        if self._storage_mode == "LOCAL":
            logger.info(
                "oci.modo_local",
                ruta=str(LOCAL_STORAGE_DIR),
            )
            LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
            self._initialized = True
            return

        if self._storage_mode != "OCI":
            raise StorageUnavailableError(
                f"Modo de almacenamiento no soportado: {self._storage_mode}."
            )
        if not self._settings.oci_configured:
            raise StorageUnavailableError(
                "El modo OCI está activo pero sus credenciales no están configuradas."
            )

        try:
            import oci

            config = {
                "user": self._settings.oci_user_ocid,
                "tenancy": self._settings.oci_tenancy_ocid,
                "region": self._settings.oci_region,
                "fingerprint": self._settings.oci_fingerprint,
                "key_file": self._settings.oci_private_key_path,
            }
            self._client = oci.object_storage.ObjectStorageClient(config)
            self._initialized = True
            logger.info("oci.inicializado", region=self._settings.oci_region)
        except ImportError as exc:
            raise StorageUnavailableError("El SDK de OCI no está instalado.") from exc
        except Exception as exc:
            logger.error("oci.inicializacion.error", error=str(exc))
            raise StorageUnavailableError("No se pudo inicializar OCI Object Storage.") from exc

    async def guardar_documento(
        self,
        objeto_key: str,
        contenido: str | bytes,
        content_type: str = "application/json",
    ) -> bool:
        """
        Guarda un documento (original o resultado) en OCI Object Storage o en almacenamiento local.

        Args:
            objeto_key: Ruta del objeto (ej: "recibidos/DOC-001.pdf" o "resultados/DOC-001.json")
            contenido: Contenido del archivo como string o bytes
            content_type: MIME type del contenido

        Returns:
            True si se guardó correctamente
        """
        await self._inicializar()
        if self._storage_mode == "LOCAL":
            try:
                local_file = LOCAL_STORAGE_DIR / objeto_key
                local_file.parent.mkdir(parents=True, exist_ok=True)
                if isinstance(contenido, bytes):
                    local_file.write_bytes(contenido)
                else:
                    local_file.write_text(contenido, encoding="utf-8")
                logger.info(
                    "oci.local.guardado",
                    key=objeto_key,
                    path=str(local_file),
                    bytes=len(contenido),
                )
            except Exception as err:
                logger.error("oci.local.escritura_error", key=objeto_key, error=str(err))
                raise StoragePersistenceError(
                    f"No se pudo guardar '{objeto_key}' en almacenamiento local."
                ) from err
            if isinstance(contenido, str):
                self._mock_store[objeto_key] = contenido
            return True

        client = self._client
        if client is None:
            raise StorageUnavailableError("El cliente OCI no fue inicializado.")
        try:
            body_bytes = contenido if isinstance(contenido, bytes) else contenido.encode("utf-8")
            client.put_object(
                namespace_name=self._settings.oci_namespace,
                bucket_name=self._settings.oci_bucket_name,
                object_name=objeto_key,
                put_object_body=io.BytesIO(body_bytes),
                content_type=content_type,
            )
            logger.info("oci.guardado", key=objeto_key)
            return True
        except Exception as exc:
            logger.error("oci.guardar.error", key=objeto_key, error=str(exc))
            raise StoragePersistenceError(
                f"No se pudo guardar '{objeto_key}' en OCI Object Storage."
            ) from exc

    async def obtener_documento(self, objeto_key: str) -> str | None:
        """Obtiene el contenido de un objeto del bucket o del disco local."""
        await self._inicializar()
        if self._storage_mode == "LOCAL":
            if objeto_key in self._mock_store:
                return self._mock_store[objeto_key]
            local_file = LOCAL_STORAGE_DIR / objeto_key
            if local_file.exists():
                return local_file.read_text(encoding="utf-8")
            return None

        client = self._client
        if client is None:
            raise StorageUnavailableError("El cliente OCI no fue inicializado.")
        try:
            response = client.get_object(
                namespace_name=self._settings.oci_namespace,
                bucket_name=self._settings.oci_bucket_name,
                object_name=objeto_key,
            )
            return response.data.text
        except Exception as exc:
            if getattr(exc, "status", None) == 404:
                return None
            logger.error("oci.obtener.error", key=objeto_key, error=str(exc))
            raise StorageUnavailableError(
                f"No se pudo consultar '{objeto_key}' en OCI Object Storage."
            ) from exc

    async def listar_documentos(self, prefix: str = "") -> list[str]:
        """Lista objetos en el bucket o en el disco local con un prefijo dado."""
        await self._inicializar()
        if self._storage_mode == "LOCAL":
            keys = set(self._mock_store.keys())
            search_dir = LOCAL_STORAGE_DIR / prefix
            if search_dir.exists():
                for p in search_dir.rglob("*.json"):
                    rel_path = str(p.relative_to(LOCAL_STORAGE_DIR)).replace("\\", "/")
                    keys.add(rel_path)
            return [k for k in keys if k.startswith(prefix)]

        client = self._client
        if client is None:
            raise StorageUnavailableError("El cliente OCI no fue inicializado.")
        try:
            response = client.list_objects(
                namespace_name=self._settings.oci_namespace,
                bucket_name=self._settings.oci_bucket_name,
                prefix=prefix,
            )
            return [obj.name for obj in response.data.objects]
        except Exception as exc:
            logger.error("oci.listar.error", prefix=prefix, error=str(exc))
            raise StorageUnavailableError(
                "No se pudieron listar los documentos en OCI Object Storage."
            ) from exc

    @property
    def disponible(self) -> bool:
        return self._initialized and (self._storage_mode == "LOCAL" or self._client is not None)
