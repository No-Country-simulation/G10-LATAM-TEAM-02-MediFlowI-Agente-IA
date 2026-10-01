# 🔐 Guía Oficial de Seguridad: Gestión de Secretos y Variables de Entorno en MediFlow

Esta guía detalla las buenas prácticas, comandos de consola y políticas de seguridad para gestionar credenciales, API Keys y variables sensibles en **MediFlow**, garantizando que **ningún secreto quede expuesto en el repositorio Git**.

---

## 🚫 1. Lo que NUNCA debe quedar en el repositorio

Los siguientes elementos tienen estrictamente prohibido ser añadidos al control de versiones (`git add`):

| Categoría | Elementos Sensibles | Riesgo de Exposición |
|---|---|---|
| **Proveedores LLM** | `GOOGLE_API_KEY`, `OPENAI_API_KEY` | Facturación no autorizada, agotamiento de cuotas, revocación inmediata por escáners de GitHub. |
| **Infraestructura Cloud (OCI)** | Llaves privadas `.pem` (`oci_api_key.pem`), User OCID, Fingerprint, Tenancy OCID | Compromiso total del tenancy de Oracle Cloud Infrastructure. |
| **Base de Datos** | `DATABASE_URL`, contraseñas de PostgreSQL (`mediflow_dev`, producción) | Acceso y robo de Historias Clínicas Electrónicas y datos médicos sensibles. |
| **Sesiones y Tokens** | `SECRET_KEY`, JWT secrets, tokens de sesión Bearer | Suplantación de identidad y escalamiento de privilegios RBAC. |
| **Protocolo MCP** | `VITE_MCP_API_KEY`, tokens de autorización de herramientas externas | Ejecución remota de herramientas sin auditoría. |
| **Archivos de Entorno** | `.env`, `.env.local`, `.env.production` | Exposición consolidada de toda la configuración del sistema. |

> [!IMPORTANT]
> El archivo [`.gitignore`](.gitignore) del proyecto ya está preconfigurado para ignorar `.env`, `.env.local`, `*.pem`, `*.key` y carpetas de storage local. **Nunca uses `git add -f` (force) sobre estos archivos.**

---

## 💻 2. Cómo Inyectar Secretos en Consola (Sin guardarlos en historial)

### A. En Windows (PowerShell)

#### Opción 1: Variable en la sesión actual de PowerShell (Volátil)
Esta variable solo vivirá mientras la ventana de la terminal esté abierta y se destruye al cerrarla:
```powershell
# Inyectar temporalmente en la sesión actual
$env:GOOGLE_API_KEY = "tu_clave_real_aqui"
$env:DATABASE_URL = "postgresql://postgres:tu_password@localhost:5432/mediflow_dev"

# Verificar que existe sin imprimir el valor sensible en pantalla
Test-Path env:GOOGLE_API_KEY
```

#### Opción 2: Entrada interactiva oculta (Evita que la clave quede en el historial de comandos)
PowerShell guarda los comandos ejecutados en el historial (`Get-History` o archivo `ConsoleHost_history.txt`). Para evitar que la clave quede guardada en texto plano:
```powershell
# Solicita la clave de forma oculta (sin mostrar los caracteres al escribir)
$secureKey = Read-Host -Prompt "Ingresa tu Google API Key de forma segura" -AsSecureString
$bstr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureKey)
$env:GOOGLE_API_KEY = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($bstr)
```

---

### B. En Linux / macOS (Bash o Zsh)

#### Opción 1: Anteponer un espacio antes del comando
En la mayoría de terminales Unix configuradas con `HISTCONTROL=ignorespace`, cualquier comando que empiece con un espacio **NO se guarda en el historial (`~/.bash_history` o `~/.zsh_history`)**:
```bash
# Nota el espacio inicial antes de 'export':
 export GOOGLE_API_KEY="tu_clave_real_aqui"
 export DATABASE_URL="postgresql://postgres:password@localhost:5432/mediflow_dev"
```

#### Opción 2: Entrada interactiva silenciosa (`read -s`)
```bash
read -s -p "Ingresa tu GOOGLE_API_KEY: " MI_KEY && export GOOGLE_API_KEY="$MI_KEY"
echo "" # Salto de línea
```

---

### C. En GitHub Actions (GitHub CLI `gh`)

Para pipelines de CI/CD, inyecta los secretos directamente en el repositorio remoto usando el CLI oficial de GitHub sin guardarlos en ningún archivo local:
```bash
# Configurar API Key en GitHub Secrets
gh secret set GOOGLE_API_KEY --body "tu_clave_real_aqui"

# O de forma interactiva (más seguro):
gh secret set DATABASE_URL
```

---

## 🐳 3. Configuración Segura con Docker y Docker Compose

En [docker-compose.yml](infrastructure/docker/docker-compose.yml), las variables de entorno están parametrizadas para leerse desde el entorno del host o desde un archivo `.env` local no versionado:

```yaml
# infrastructure/docker/docker-compose.yml
services:
  backend:
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - DATABASE_URL=${DATABASE_URL}
      - STORAGE_MODE=LOCAL
```

### Flujo de Trabajo Recomendado:
1. Copia la plantilla de ejemplo:
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
2. Edita `backend/.env` y `frontend/.env` con tus credenciales reales.
3. Verifica que Git los ignore ejecutando:
   ```bash
   git status
   ```
   *Ni `backend/.env` ni `frontend/.env` deben aparecer en la lista de archivos para commit.*

---

## 🧩 4. Integración con Model Context Protocol (MCP) en Frontend

Para conectar el Frontend con servidores de herramientas MCP:
1. Revisa la plantilla [frontend/.env.example](frontend/.env.example):
   ```env
   VITE_MCP_ENABLED=true
   VITE_MCP_SERVER_URL=http://localhost:8001/mcp
   VITE_MCP_API_KEY=tu_api_key_mcp_aqui
   ```
2. El frontend consume estas credenciales mediante el módulo centralizado:
   - [frontend/src/config/mcp.config.ts](frontend/src/config/mcp.config.ts): Lee de forma segura `import.meta.env` y valida la integridad de la conexión.
   - [frontend/src/api/mcp.api.ts](frontend/src/api/mcp.api.ts): Expone `listMcpTools` y `callMcpTool` con headers de autenticación automáticos.

---

## 🔍 5. Checklist Preventivo antes de cada `git commit`

Antes de hacer un commit o abrir un Pull Request, ejecuta siempre:

1. **Revisar archivos en stage**:
   ```bash
   git status
   ```
2. **Inspeccionar exactamente las líneas que se van a guardar**:
   ```bash
   git diff --staged
   ```
   *Asegúrate de que no haya cadenas como `AIzaSy...`, `BEGIN PRIVATE KEY`, contraseñas de base de datos o URLs con credenciales embebidas.*

---

## 🚨 6. Protocolo de Emergencia si se filtra un Secreto por Error

Si accidentalmente commiteaste o subiste una credencial a GitHub:

1. **REVOCAR INMEDIATAMENTE** la clave en la consola del proveedor (Google Cloud / AI Studio, OpenAI, Oracle Cloud). *Asume que cualquier clave subida a GitHub ya fue copiada por bots en menos de 10 segundos.*
2. **Generar una nueva clave** y configurarla en tus variables de entorno locales.
3. **Eliminar el secreto del historial Git**:
   ```bash
   # Si el commit aún es local (no hiciste push):
   git reset --soft HEAD~1
   # Corrige el archivo y vuelve a commitear
   ```
   Si ya hiciste push a GitHub, debes usar herramientas como `git-filter-repo` o `bfg-repo-cleaner` para purgar el historial y forzar el push (`git push --force`).
