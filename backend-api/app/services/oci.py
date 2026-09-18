"""
Servicio de integración con Oracle Cloud Infrastructure (OCI Object Storage)
Soporta:
1. Autenticación por Instance Principal (Seguridad máxima en OCI Compute VM Always Free)
2. Autenticación local mediante archivo ~/.oci/config
3. Modo Simulación Local (Mock) para desarrollo sin credenciales
"""
import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class OCISignatureStorage:
    def __init__(self):
        self.bucket_name = os.getenv("OCI_BUCKET_NAME", "mediflow-documentos-clinicos")
        self.namespace = os.getenv("OCI_NAMESPACE", "mediflow_ns")
        self.mock_mode = os.getenv("OCI_MOCK_MODE", "true").lower() == "true"
        self.client = None

        if not self.mock_mode:
            try:
                import oci
                # Intentar primero Instance Principal (para VM de OCI)
                try:
                    signer = oci.auth.signers.InstancePrincipalsSecurityTokenSigner()
                    self.client = oci.object_storage.ObjectStorageClient(config={}, signer=signer)
                    logger.info("OCI: Autenticado exitosamente mediante Instance Principal")
                except Exception as ip_err:
                    logger.warning(f"OCI: No se pudo usar Instance Principal: {ip_err}. Intentando ~/.oci/config...")
                    config = oci.config.from_file(
                        file_location=os.getenv("OCI_CONFIG_FILE", "~/.oci/config"),
                        profile_name=os.getenv("OCI_CONFIG_PROFILE", "DEFAULT")
                    )
                    self.client = oci.object_storage.ObjectStorageClient(config)
                    logger.info("OCI: Autenticado mediante archivo de configuración local")
            except Exception as e:
                logger.error(f"OCI: Error inicializando cliente real ({e}). Activando Mock Mode.")
                self.mock_mode = True

    def subir_documento(self, ruta_objeto: str, contenido_json: Dict[str, Any]) -> Dict[str, str]:
        """
        Sube un objeto JSON estructurado al Object Storage segregado por estado.
        """
        if self.mock_mode:
            logger.info(f"[OCI MOCK] Guardando documento en bucket '{self.bucket_name}': {ruta_objeto}")
            mock_dir = os.path.join("data_mock_oci", os.path.dirname(ruta_objeto))
            os.makedirs(mock_dir, exist_ok=True)
            mock_file = os.path.join("data_mock_oci", ruta_objeto)
            with open(mock_file, "w", encoding="utf-8") as f:
                json.dump(contenido_json, f, indent=2, ensure_ascii=False)
            return {
                "bucket": self.bucket_name,
                "ruta_objeto": ruta_objeto,
                "status_backup": "exito"
            }

        try:
            body_bytes = json.dumps(contenido_json, ensure_ascii=False).encode("utf-8")
            self.client.put_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket_name,
                object_name=ruta_objeto,
                put_object_body=body_bytes,
                content_type="application/json"
            )
            logger.info(f"OCI: Objeto subido exitosamente: {ruta_objeto}")
            return {
                "bucket": self.bucket_name,
                "ruta_objeto": ruta_objeto,
                "status_backup": "exito"
            }
        except Exception as err:
            logger.error(f"OCI: Error subiendo objeto a {ruta_objeto}: {err}")
            return {
                "bucket": self.bucket_name,
                "ruta_objeto": ruta_objeto,
                "status_backup": "fallido"
            }

oci_service = OCISignatureStorage()
