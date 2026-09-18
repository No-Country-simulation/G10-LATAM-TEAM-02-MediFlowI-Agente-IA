# 🔄 Guía de Flujo de Trabajo (Workflow) – MediFlow
**Metodología:** Schema-Driven Development (SDD)  
**Proyecto:** MediFlow – Hackathon ONE G10  
**Repositorio Oficial:** [`https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA`](https://github.com/No-Country-simulation/G10-LATAM-TEAM-02-MediFlowI-Agente-IA)  
**Equipo:** 8 Integrantes  
**Versión del Documento:** 2.0.0  

---

## 1. Convención de Commits (Conventional Commits 1.0.0)

Para garantizar un historial de Git limpio, semántico y profesional (evaluado en el pliego de la hackathon), todo commit debe seguir el formato estándar:

```text
<tipo>(<alcance>): <descripción concisa en modo imperativo y minúsculas>

[cuerpo explicativo opcional del contexto o justificación técnica]

[referencias opcionales: Closes #12 o Ref #T-06]
```

### 1.1 Tipos Permitidos

| Tipo | Propósito | Ejemplo |
|---|---|---|
| `feat` | Nueva funcionalidad clínica o técnica | `feat(T-10): implementar webhook de triaje en n8n` |
| `fix` | Corrección de un error, bug o schema | `fix(T-05): corregir formato regex de cie10 en pydantic` |
| `docs` | Cambios en documentación | `docs(T-16): anadir diagrama de arquitectura al README` |
| `test` | Inclusión o ajuste de datasets y pruebas | `test(T-03): agregar caso 2 de urgencia tromboembolismo` |
| `refactor` | Mejora de código sin cambiar funcionalidad | `refactor(T-07): modularizar reglas del motor de enrutamiento` |
| `chore` | Tareas de configuración, tooling y dependencias | `chore(T-01): anadir variables de entorno en env.example` |
| `style` | Formato, espacios en blanco, estilos CSS/UI | `style(T-13): ajustar paleta semantica de badges de prioridad` |

### 1.2 Alcances (Scopes) del Proyecto
El alcance debe corresponder al **ID de la tarea consolidada** (`T-01` a `T-13`) o al área técnica afectada:
* `(T-XX)`: Ejemplo `feat(T-04): prompt de extraccion multimodal`.
* `(schemas)`, `(n8n)`, `(gemini)`, `(oci)`, `(frontend)`, `(datasets)`, `(docs)`.

---

## 2. Versionamiento Semántico (SemVer 2.0.0)

El proyecto utiliza tags de Git siguiendo la especificación **`vMAJOR.MINOR.PATCH`**:

* **MAJOR (`v1.0.0`):** Release oficial final listo para evaluación de los jueces.
* **MINOR (`v0.X.0`):** Entrega de un hito o épica funcional completa.
* **PATCH (`v0.X.Y`):** Correcciones de bugs o ajustes en schemas/prompts.

### Matriz de Hitos y Versiones
* **`v0.1.0` (Hito 1):** Especificación SDD, OpenAPI 3.0.3 validado, HUs y Backlog inicial (`T-01`).
* **`v0.2.0` (Hito 2):** Datasets clínicos oficiales (`T-02`) y modelos Pydantic v2 (`T-03`).
* **`v0.3.0` (Hito 3):** Agente Gemini (`T-04`), motor de routing (`T-05`) y persistencia OCI (`T-09`).
* **`v0.4.0` (Hito 4):** Automatización en n8n y alertas (`T-06`).
* **`v0.5.0` (Hito 5):** UI en React (Vite) con visualizador Split-Screen (`T-11`) y panel HITL (`T-07`).
* **`v1.0.0` (Hito Final):** Pruebas de contrato (`T-08`), despliegue OCI (`T-10`), documentación final (`T-12`) y pitch demo (`T-13`).

---

## 3. Ciclo de Vida del Desarrollo en 7 Pasos (Paso a Paso)

Para coordinar eficientemente a los 8 integrantes del equipo, cada tarea del backlog sigue estrictamente este flujo:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. ASIGNACIÓN                                               │
│    Team Leader asigna Issue en GitHub o miembro se autoasigna│
│    Estado: 👤 status: assigned                              │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. SETUP DE RAMA                                            │
│    git checkout develop && git pull origin develop          │
│    git checkout -b feature/T-XX-descripcion                 │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. IMPLEMENTACIÓN LOCAL                                     │
│    Desarrollo siguiendo los contratos en schemas/           │
│    Commits convencionales: git commit -m "feat(T-XX): ..."  │
│    Estado: 🔨 status: in-progress                           │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. SINCRONIZACIÓN OBLIGATORIA CON DEVELOP (Evitar conflictos│
│    git checkout develop && git pull origin develop          │
│    git checkout feature/T-XX-descripcion                    │
│    git merge develop                                        │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. PUSH Y APERTURA DE PULL REQUEST                          │
│    git push -u origin feature/T-XX-descripcion              │
│    Crear PR usando la plantilla hacia 'develop'             │
│    Incluir 'Closes #XX' para auto-cierre                    │
│    Estado: 🔍 status: in-review                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. CODE REVIEW & APROBACIÓN                                 │
│    Team Leader o par revisa criterios de aceptación y schema│
│    Si hay observaciones: corregir en la misma rama          │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. CIERRE Y MERGE (Squash and Merge)                        │
│    Merge a develop mediante Squash and Merge                │
│    Eliminar rama remota                                     │
│    El Issue se cierra automáticamente y pasa a ✅ Done      │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. Detalle de Comandos para Cada Integrante

### Paso 1 — Asignación y Selección
Revisar [`docs/backlog.md`](backlog.md) o el tablero de GitHub Projects. Tomar un Issue sin dependencias pendientes y asignar la etiqueta `status: assigned`.

### Paso 2 — Setup de Rama
```bash
git checkout develop
git pull origin develop
git checkout -b feature/T-06-gemini-extractor
```
> **Regla:** Siempre crear la rama desde `develop` actualizado. Nunca desde otra rama de desarrollo.

### Paso 3 — Implementación y Commits
```bash
# Modificar archivos...
git add .
git commit -m "feat(T-06): prompt de extraccion clinica con Gemini"
```

### Paso 4 — Sincronización Obligatoria con `develop`
Antes de abrir el PR, sincronizar con lo que otros compañeros hayan mergeado:
```bash
git checkout develop
git pull origin develop
git checkout feature/T-06-gemini-extractor
git merge develop
```
* **Si NO hay conflictos:** Continuar al siguiente paso.
* **Si HAY conflictos:** Resolverlos manualmente en el editor, guardar y:
  ```bash
  git add .
  git commit -m "chore(T-06): resolver conflictos con main"
  ```

### Paso 5 — Push y Apertura de PR
```bash
git push -u origin feature/T-06-gemini-extractor
```
1. Ir al repositorio en GitHub y hacer clic en **"Compare & pull request"**.
2. Completar los campos de la plantilla (ID de Tarea, Criterios de aceptación cumplidos y `Closes #XX`).
3. Asignar el reviewer (Team Leader o par).

### Paso 6 — Code Review
Si el reviewer solicita cambios:
```bash
# Corregir en la misma rama (no crear rama nueva)
git add .
git commit -m "fix(T-06): corregir tipo de retorno en extraccion"
git push origin feature/T-06-gemini-extractor
```
El Pull Request se actualiza automáticamente.

### Paso 7 — Cierre
El Team Leader o revisor aprueba y ejecuta **Squash and Merge**. El issue vinculado se cierra solo en GitHub Projects.

---

## 5. Configuración del Repositorio en GitHub

### 5.1 Reglas de Protección de `main` (Branch Protection)
Configurar en GitHub: *Settings → Branches → Branch protection rules* para `main`:
* [x] **Require a pull request before merging**
* [x] **Require approvals (1 mínimo)**
* [x] **Dismiss stale pull request approvals when new commits are pushed**
* [ ] Do not allow bypassing the above settings

### 5.2 Estrategia de Merge Recomendada
* **Squash and Merge:** Combina todos los commits del PR en uno solo en `main`, manteniendo el historial limpio y legible:
  ```text
  feat(T-06): prompt de extraccion multimodal con Gemini (#12)
  ```

### 5.3 Automatización del Tablero (GitHub Projects v2)
Para que las tarjetas se muevan de forma 100% automática sin intervención manual:
1. En tu GitHub Project, haz clic en **Workflows** (icono de rayo ⚡ o menú de tres puntos).
2. **Auto-move to In Review:**
   * Activar la regla predefinida: *"When a pull request is opened or reopened"* ➔ **Set Status: 🔍 In Review**.
3. **Auto-move to Done:**
   * Activar la regla predefinida: *"When an item is closed"* (disparado automáticamente por `Closes #XX` al mergear el PR) ➔ **Set Status: ✅ Done**.


---

## 6. Automatización de Issues con GitHub CLI (`gh`)

El repositorio incluye el script [`scripts/crear-issues.sh`](file:///home/wigsdev/GitHub/mediflow/scripts/crear-issues.sh) que crea automáticamente todas las etiquetas y los 18 issues del proyecto:

```bash
# Dar permisos y ejecutar
chmod +x scripts/crear-issues.sh
./scripts/crear-issues.sh
```

---

## 7. Política de Reasignación y Comunicación (Equipo de 8)

| Situación | Acción Inmediata |
|---|---|
| **Bloqueo técnico > 1 hora** | Avisar en el chat grupal o etiquetar al Team Leader en el Issue. No esperar al deadline. |
| **Falta de disponibilidad temporal** | Si un integrante se complica de horario, libera el Issue cambiando el label a `status: assigned` o reasignando a otro compañero. |
| **Dudas sobre datos clínicos o CIE-10** | Consultar [`schemas/clinical_extraction.json`](../schemas/clinical_extraction.json) antes de modificar código. |
| **Canal de comunicación técnica** | Pull Requests e Issues de GitHub (toda decisión queda registrada para el jurado). |
