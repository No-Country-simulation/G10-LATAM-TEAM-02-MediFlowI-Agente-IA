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
import structlog
from app.core.config import Settings

logger = structlog.get_logger(__name__)


class OCIStorageRepository:
    """
    Repositorio para OCI Object Storage.

    En modo desarrollo (sin credenciales OCI configuradas),
    opera en modo 'local mock' que guarda en memoria.
    """

    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = None
        self._mock_store: dict[str, str] = {}  # fallback dev
        self._inicializar()

    def _inicializar(self):
        """Inicializa el cliente OCI si las credenciales están disponibles."""
        if not self._settings.oci_configured:
            logger.warning(
                "oci.modo_mock",
                razon="OCI no configurado. Usando almacenamiento en memoria.",
            )
            return

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
            logger.info("oci.inicializado", region=self._settings.oci_region)
        except ImportError:
            logger.warning("oci.sdk.no_disponible", fallback="mock")
        except Exception as exc:
            logger.error("oci.inicializacion.error", error=str(exc))

    async def guardar_documento(
        self,
        objeto_key: str,
        contenido: str,
        content_type: str = "application/json",
    ) -> bool:
        """
        Guarda un documento en OCI Object Storage.

        Args:
            objeto_key: Ruta del objeto (ej: "procesados/urgentes/DOC-001.json")
            contenido: Contenido del archivo como string
            content_type: MIME type del contenido

        Returns:
            True si se guardó correctamente
        """
        if self._client is None:
            # Mock: guardar en memoria
            self._mock_store[objeto_key] = contenido
            logger.info("oci.mock.guardado", key=objeto_key, bytes=len(contenido))
            return True

        try:
            import oci
            self._client.put_object(
                namespace_name=self._settings.oci_namespace,
                bucket_name=self._settings.oci_bucket_name,
                object_name=objeto_key,
                put_object_body=io.BytesIO(contenido.encode("utf-8")),
                content_type=content_type,
            )
            logger.info("oci.guardado", key=objeto_key)
            return True
        except Exception as exc:
            logger.error("oci.guardar.error", key=objeto_key, error=str(exc))
            raise

    async def obtener_documento(self, objeto_key: str) -> str | None:
        """Obtiene el contenido de un objeto del bucket."""
        if self._client is None:
            return self._mock_store.get(objeto_key)

        try:
            import oci
            response = self._client.get_object(
                namespace_name=self._settings.oci_namespace,
                bucket_name=self._settings.oci_bucket_name,
                object_name=objeto_key,
            )
            return response.data.text
        except Exception as exc:
            logger.error("oci.obtener.error", key=objeto_key, error=str(exc))
            return None

    async def listar_documentos(self, prefix: str = "") -> list[str]:
        """Lista objetos en el bucket con un prefijo dado."""
        if self._client is None:
            return [k for k in self._mock_store if k.startswith(prefix)]

        try:
            import oci
            response = self._client.list_objects(
                namespace_name=self._settings.oci_namespace,
                bucket_name=self._settings.oci_bucket_name,
                prefix=prefix,
            )
            return [obj.name for obj in response.data.objects]
        except Exception as exc:
            logger.error("oci.listar.error", prefix=prefix, error=str(exc))
            return []

    @property
    def disponible(self) -> bool:
        return self._client is not None
