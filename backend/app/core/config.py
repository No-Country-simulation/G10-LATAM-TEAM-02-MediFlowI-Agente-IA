"""
MediFlow — Configuración central de la aplicación.

Todas las variables de entorno se leen aquí con pydantic-settings.
NUNCA hardcodear valores sensibles en el código.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    # ── API Security ─────────────────────────────────────────────────────────
    api_key: str = "mediflow-dev-secret"

    # ── LLM ──────────────────────────────────────────────────────────────────
    google_api_key: str = ""
    gemini_model: str = "gemini-1.5-flash"
    openai_api_key: str = ""

    # ── OCI Object Storage ───────────────────────────────────────────────────
    oci_user_ocid: str = ""
    oci_tenancy_ocid: str = ""
    oci_region: str = "sa-saopaulo-1"
    oci_fingerprint: str = ""
    oci_private_key_path: str = "/app/oci_private_key.pem"
    oci_namespace: str = ""
    oci_bucket_name: str = "mediflow-documentos-clinicos"

    # ── Umbrales del Agente ───────────────────────────────────────────────────
    confidence_threshold_high: float = 0.8
    confidence_threshold_low: float = 0.5

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"

    @property
    def oci_configured(self) -> bool:
        return bool(self.oci_user_ocid and self.oci_namespace)

    @property
    def llm_configured(self) -> bool:
        return bool(self.google_api_key or self.openai_api_key)


@lru_cache
def get_settings() -> Settings:
    """Retorna instancia singleton de Settings (cacheada)."""
    return Settings()
