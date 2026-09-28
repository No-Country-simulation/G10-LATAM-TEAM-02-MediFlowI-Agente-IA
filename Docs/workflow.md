# 🔄 Flujo de Trabajo Git & Colaboración — MediFlow

> **Proyecto:** MediFlow — Agente Autónomo de Triaje Clínico  
> **Programa:** Hackathon ONE G10 (Oracle & Alura) · Simulación Laboral No Country  
> **Convención:** Git Flow Adaptado a Ramas Personales por Colaborador  
> **Fecha:** Septiembre - Octubre 2026  
> **Estado:** Documento Oficial de Referencia Técnica  

---

## 1. Visión General del Modelo de Ramas

Para garantizar orden, trazabilidad y evitar sobrecarga en la creación de múltiples ramas efímeras, el equipo ha acordado de forma unánime un esquema de **Ramas Personales por Colaborador**:

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        TOPOLOGÍA DE RAMAS MEDIFLOW                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                        │
│   [ main ]  (Producción estable / Entrega final al Hackathon)          │
│      ▲                                                                 │
│      │  (PR de Cierre de Sprint con tag de versión / release)          │
│   [ develop ]  (Rama central de integración de todo el equipo)         │
│      ▲                                                                 │
│      ├─────── Pull Request (Squash and Merge) ─────────────┐          │
│      │                                                     │          │
│  [ dev-wilmer-gulcochia ]      [ dev-erick-pariona ]   [ dev-... ]     │
│  (Rama personal de trabajo)    (Rama personal)         (Ramas pers.)   │
│                                                                        │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Mapa Oficial de Ramas del Repositorio

El repositorio remoto cuenta con las siguientes ramas activas:

| Rama | Tipo | Propietario / Rol | Propósito |
|---|---|---|---|
| **`main`** | Tronco Principal | Todo el equipo | Código de producción probado, sellado de releases (`v1.0.0`) y entregable para el jurado. |
| **`develop`** | Integración | Todo el equipo | Rama central donde converge el trabajo de todos los colaboradores mediante PRs revisados. |
| **`dev-wilmer-gulcochia`** | Personal | Wilmer Gulcochia (Tech Lead / Backend) | Desarrollo local, specs, orquestación y backend core. |
| **`dev-erick-pariona`** | Personal | Erick Pariona (Backend Developer) | Endpoints FastAPI, parsing de documentos y servicios backend. |
| **`dev-krystopher`** | Personal | Kristopher (Backend & AI / LLM) | Nodos de LangGraph, integración con Gemini y lógica de triaje. |
| **`dev-Jefte-Reyes`** | Personal | Jefte Reyes (AI / LLM & Data Engineer) | Ingeniería de prompts, calibración de scoring y modelos LLM. |
| **`dev-front-damaris-quiroz`**| Personal | Damaris Quiroz (Frontend Developer) | UI React, componentes de triaje y visor clínico. |
| **`dev-samuel-junieles`** | Personal | Samuel Junieles (Frontend & UI/UX) | Sistema de diseño, maquetación, estados de carga y UX. |
| **`dev-alonso-carbajal`** | Personal | Alonso Carbajal (QA Engineer) | Contract testing con Schemathesis, suites Pytest y validación E2E. |
| **`dev-henry-suarez`** | Personal | Henry Suarez (DevOps & Cloud) | Docker Compose, OCI Object Storage, proxy Nginx y CI/CD. |

---

## 3. Ciclo de Trabajo Diario Paso a Paso (Paso a Paso)

Cada colaborador trabajará en su respectiva rama personal siguiendo este ciclo para evitar conflictos de código:

### Paso 1: Actualizar la rama local antes de programar
Antes de empezar una nueva tarea o Historia de Usuario, asegúrate de traer lo último integrado en `develop`:

```bash
# 1. Asegúrate de estar en tu rama personal
git checkout dev-<tu-nombre>

# 2. Descarga los últimos cambios del repositorio remoto
git fetch origin

# 3. Sincroniza e integra lo que el equipo mergeó en develop
git merge origin/develop
```

> 💡 **Tip:** Si hay conflictos al hacer merge desde `origin/develop`, resuélvelos localmente antes de continuar programando.

---

### Paso 2: Desarrollar y realizar commits atómicos
Trabaja en los archivos correspondientes a la Historia de Usuario asignada. Usa la convención de **Conventional Commits**:

```bash
# Añade los archivos modificados
git add <archivos-modificados>

# Crea el commit referenciando la US correspondiente
git commit -m "feat(US-04): implementar parsing de documentos clinicos con pymupdf"
```

#### Prefijos de Commits permitidos:
* `feat(...)`: Nueva funcionalidad (código nuevo para una US).
* `fix(...)`: Corrección de un bug o error.
* `test(...)`: Añadir o actualizar pruebas unitarias o de contrato.
* `docs(...)`: Cambios en documentación o especificaciones.
* `refactor(...)`: Mejoras de código sin cambiar funcionalidad.
* `build(...)` / `ci(...)`: Configuración de Docker, Makefile o GitHub Actions.

---

### Paso 3: Subir los cambios a tu rama remota
Publica tus avances en GitHub:

```bash
git push origin dev-<tu-nombre>
```

---

### Paso 4: Abrir Pull Request hacia `develop`
Una vez completados los criterios de aceptación de tu Historia de Usuario:

1. Ve a GitHub y abre un **Pull Request**:
   * **Base branch (Destino):** `develop`
   * **Compare branch (Origen):** `dev-<tu-nombre>`
2. **Título del PR:** Debe seguir el formato acordado:
   ```text
   feat(US-04): Ingestión y parsing de documentos clínicos con PyMuPDF
   ```
3. **Cuerpo del PR:**
   * Enlazar el Issue que resuelve (ej. `Closes #4` o `Resuelve #4`).
   * Describir brevemente qué cambios se implementaron.
   * Confirmar que pasa los linters y pruebas locales (`make validate`, `pytest`).

---

### Paso 5: Code Review y Merge
* Al menos **un par técnico o el Tech Lead** debe revisar y aprobar el PR.
* Estrategia de fusión: **Squash and merge** (mantiene el historial de `develop` limpio y ordenado).
* ⚠️ **Importante:** Al hacer el merge, **NO elimines tu rama personal** (ya que la seguirás usando para las siguientes historias del sprint).

---

## 4. Reglas de Oro de Convivencia Técnica

1. **Nunca hacer push directo a `develop` ni a `main`:** Todo cambio entra exclusivamente vía Pull Request.
2. **Respetar el Contrato OpenAPI:** Si una tarea requiere agregar o modificar un endpoint, primero se discute y actualiza `specs/openapi.yaml` y luego se regenera el código (`make generate`).
3. **Validación previa:** Antes de subir tu PR, ejecuta en local:
   ```bash
   # Si tocas OpenAPI o Backend:
   make validate
   pytest backend/tests/
   ```
4. **Registro en Plataforma No Country (Regla del 50% / 20%):** Cada vez que completes una US o hagas un PR aprobado, registra tu avance en la plataforma de No Country para asegurar tu métrica individual de participación.
