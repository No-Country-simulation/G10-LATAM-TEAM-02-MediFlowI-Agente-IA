FROM python:3.11-slim-bookworm

WORKDIR /app

# Dependencias nativas: OCR real en español, health check y manejo de señales.
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-spa \
    ca-certificates \
    curl \
    tini \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    APP_ENV=production \
    LOG_LEVEL=INFO \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

COPY pyproject.toml README.md alembic.ini ./
COPY app ./app
COPY alembic ./alembic

# Producción instala solo librerías de ejecución; desarrollo puede incluir pytest,
# Ruff, mypy y las herramientas de contrato con --build-arg INSTALL_DEV=true.
ARG INSTALL_DEV=false
RUN python -m pip install --upgrade pip setuptools wheel && \
    if [ "$INSTALL_DEV" = "true" ]; then \
      python -m pip install ".[dev]"; \
    else \
      python -m pip install .; \
    fi

RUN addgroup --system mediflow && \
    adduser --system --ingroup mediflow --home /app mediflow && \
    mkdir -p /app/storage && \
    chown -R mediflow:mediflow /app

USER mediflow

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail --silent --show-error http://localhost:8000/health >/dev/null || exit 1

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
