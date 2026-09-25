FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema para PyMuPDF y OCI
RUN apt-get update && apt-get install -y \
    libmupdf-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar pip actualizado
RUN pip install --upgrade pip

# Copiar definición de paquete y código fuente
COPY pyproject.toml README.md ./
COPY app/ ./app/

# Instalar paquete en modo editable con dependencias de desarrollo
RUN pip install -e ".[dev]"

# Variables de entorno por defecto
ENV APP_ENV=production
ENV LOG_LEVEL=INFO

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
