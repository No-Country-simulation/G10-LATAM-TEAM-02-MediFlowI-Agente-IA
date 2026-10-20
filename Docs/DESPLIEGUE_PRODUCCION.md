# 🚀 Despliegue en Producción — Reverse Proxy Nginx + Docker Compose (US-13)

Guía de la orquestación de producción de MediFlow: cómo se empaqueta el sistema
(Frontend + Backend + Nginx + PostgreSQL) en un único puerto `:80` y cómo se
despliega en una VM de **Oracle Cloud Infrastructure (OCI)**.

> Épica 6 — Infraestructura Cloud. Historia **US-13**.

---

## 🧭 Arquitectura de producción

Un único contenedor **Nginx** actúa como *reverse proxy* y expone el puerto `:80`.
El resto de servicios son **internos** (no publican puertos al host), evitando CORS
y puertos dispersos.

```
                 Internet / Navegador
                        │  :80
             ┌──────────▼───────────┐
             │   nginx (reverse      │   infrastructure/nginx/nginx.conf
             │   proxy, único :80)   │
             └─────┬───────────┬─────┘
          /        │           │  /api/   ·  /docs  ·  /health
   ┌──────────────▼──┐     ┌───▼────────────────┐
   │ frontend         │     │ backend (FastAPI)  │  (interno :8000)
   │ React build+nginx│     │ LangGraph + Gemini │
   │ (interno :80)    │     └───┬────────────────┘
   └──────────────────┘         │
                                ▼
                        ┌───────────────┐
                        │ postgres :5432 │  (interno)
                        └───────────────┘
                                │
                                ▼  persistencia de documentos
                        OCI Object Storage (modo OCI) / volumen local (modo LOCAL)
```

**Ruteo (en `nginx.conf`):**

| Ruta | Destino | Uso |
|---|---|---|
| `/` | `frontend` | SPA de React (con fallback a `index.html`) |
| `/api/` | `backend:8000` | API REST (base `/api/v1` según el contrato OpenAPI) |
| `/docs`, `/redoc`, `/openapi.json` | `backend:8000` | Documentación de la API |
| `/health` | `backend:8000/health` | Health check |

Incluye **headers de seguridad** (`X-Frame-Options`, `X-Content-Type-Options`,
`Referrer-Policy`, `X-XSS-Protection`, `server_tokens off`), timeouts largos para
el procesamiento de documentos y `client_max_body_size 20M` para subir PDFs.

---

## 📂 Archivos que componen US-13

| Archivo | Rol |
|---|---|
| `infrastructure/docker/docker-compose.prod.yml` | Orquesta nginx + frontend + backend + postgres para producción |
| `infrastructure/nginx/nginx.conf` | Configuración del reverse proxy |
| `Makefile` → targets `prod-docker` / `prod-docker-down` | Atajos para levantar/detener el stack |

---

## 🔑 Variables de entorno

Hay **dos ámbitos distintos** de variables. Es importante no confundirlos:

### 1. `.env` (raíz del repo) — leído por **Docker Compose**

Sustituye los `${...}` del `docker-compose.prod.yml`. `POSTGRES_PASSWORD` es
**obligatoria** (el compose falla si no está).

```bash
POSTGRES_DB=mediflow
POSTGRES_USER=mediflow
POSTGRES_PASSWORD=<contraseña fuerte>
MEDIFLOW_HTTP_PORT=80
```

### 2. `backend/.env` — leído por la **aplicación** (pydantic-settings)

Configuración interna del backend. Para arrancar (modo de almacenamiento LOCAL):

```bash
APP_ENV=production
GOOGLE_API_KEY=<tu clave real de Gemini>    # obligatoria para el agente
GEMINI_MODEL=gemini-1.5-flash
API_KEY=<clave fuerte propia>               # cambia el valor por defecto de dev
ALLOW_MOCK_LLM=false
# DATABASE_URL NO hace falta tocarla: el compose la inyecta apuntando al
# contenedor `postgres` (sobrescribe lo que haya en backend/.env).
```

Para persistir en **OCI Object Storage** agrega además:

```bash
OCI_USER_OCID=ocid1.user.oc1..xxxx
OCI_TENANCY_OCID=ocid1.tenancy.oc1..xxxx
OCI_REGION=sa-saopaulo-1
OCI_FINGERPRINT=xx:xx:...
OCI_NAMESPACE=<tu-namespace>
OCI_BUCKET_NAME=mediflow-documentos-clinicos
OCI_PRIVATE_KEY_PATH=/app/oci_private_key.pem
```

> El modo de almacenamiento (LOCAL/OCI) se cambia en caliente desde el endpoint
> `/settings` de la app; por defecto arranca en LOCAL. Para OCI basta con tener
> `OCI_USER_OCID` y `OCI_NAMESPACE` definidos **y montar la llave privada** (ver abajo).

> ⚠️ **Nunca** commitees `.env`, `backend/.env` ni los archivos `*.pem`.
> El `.gitignore` ya los ignora.

### Montaje de la llave privada OCI (solo modo OCI)

El backend busca la llave en `/app/oci_private_key.pem` **dentro del contenedor**.
Para montarla, añade al servicio `backend` en `docker-compose.prod.yml`:

```yaml
    volumes:
      - mediflow-storage:/app/storage
      - ../../backend/oci_private_key.pem:/app/oci_private_key.pem:ro   # ← llave OCI
```

---

## 💻 Levantar en local (prueba previa al deploy)

```bash
# 1. Configurar variables
cp backend/.env.example backend/.env     # si aún no existe; edita GOOGLE_API_KEY, API_KEY, APP_ENV
#    y crea el .env raíz con POSTGRES_PASSWORD (ver arriba)

# 2. Levantar el stack de producción
make prod-docker
#    equivale a:
#    docker compose -f infrastructure/docker/docker-compose.prod.yml up --build -d

# 3. Verificar
docker compose -f infrastructure/docker/docker-compose.prod.yml ps   # todos "healthy"
```

Comprobar en el navegador:

- `http://localhost` → interfaz (SPA de React)
- `http://localhost/docs` → Swagger UI
- `http://localhost/api/v1/health` → estado del servicio

Detener: `make prod-docker-down`

---

## ☁️ Desplegar en OCI Compute (Always Free)

En la VM de OCI (Ubuntu):

```bash
# 1. Docker + plugin compose
sudo apt update && sudo apt install -y docker.io docker-compose-v2 git
sudo usermod -aG docker ubuntu && newgrp docker

# 2. Abrir el puerto 80 en el firewall de la VM
sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
sudo netfilter-persistent save     # si falta: sudo apt install -y iptables-persistent

# 3. Clonar y configurar
git clone -b develop https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA mediflow
cd mediflow
cp backend/.env.example backend/.env    # editar: GOOGLE_API_KEY, API_KEY, APP_ENV=production, OCI_*
nano .env                               # crear el .env raíz con POSTGRES_PASSWORD, MEDIFLOW_HTTP_PORT=80
# (modo OCI) copiar la llave privada y montarla:
#   scp oci_private_key.pem ubuntu@IP:~/mediflow/backend/oci_private_key.pem

# 4. Levantar
make prod-docker
```

En la **consola web de OCI**: `Networking → VCN → Security Lists → Add Ingress Rule`
para el puerto **80** (Source `0.0.0.0/0`, TCP).

Verificar: `http://IP_PUBLICA`, `http://IP_PUBLICA/docs`, `http://IP_PUBLICA/api/v1/health`.

### Alineación con el contrato (SDD)

Al desplegar, actualiza el `servers:` de producción en `specs/openapi.yaml`
(`https://mediflow.oci.example.com/api/v1` → `http://IP_PUBLICA/api/v1`) y corre
`make generate` para que el cliente TypeScript del frontend apunte a producción.

---

## ✅ Criterios de aceptación de US-13

- [x] `infrastructure/nginx/nginx.conf` rutea correctamente `/` y `/api/` con headers seguros.
- [x] `docker compose up` levanta todos los servicios de forma orquestada en el puerto `:80`.
- [x] Sin errores de CORS: el frontend consume la API bajo el mismo origen (`/api/v1`).

---

## 🛠️ Troubleshooting

| Síntoma | Causa probable | Solución |
|---|---|---|
| `POSTGRES_PASSWORD variable is not set` | Falta el `.env` raíz o no se exportó | Crear `.env` en la raíz, o `export POSTGRES_PASSWORD=...`, o usar `--env-file .env` |
| `backend` queda `unhealthy` | Falla el healthcheck `/health` o error de arranque | `docker compose -f infrastructure/docker/docker-compose.prod.yml logs backend` |
| Frontend carga pero la API falla | `OCI` activado sin llave montada | Usar modo LOCAL o montar `oci_private_key.pem` (ver arriba) |
| Puerto 80 ocupado | Otro servicio usa el :80 | Cambiar `MEDIFLOW_HTTP_PORT` en el `.env` raíz |
