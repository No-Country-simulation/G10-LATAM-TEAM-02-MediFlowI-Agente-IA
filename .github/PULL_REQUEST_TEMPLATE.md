## 📌 Vinculación y Automatización de Tablero (GitHub Projects)

> 🤖 **Automatización de Ciclo de Vida del Issue:**
> - **Al abrir este PR:** El Issue vinculado se mueve a la columna **🔍 In Review**.
> - **Al hacer merge a `main`:** El Issue se cierra automáticamente y se mueve a la columna **✅ Done**.
> 
> *Para habilitar la vinculación automática, no borres la palabra clave `Closes`:*

**Issue vinculado:** Closes #<!-- Número del Issue a cerrar, ej: Closes #6 -->

| Metadato | Valor |
|---|---|
| **ID Tarea** | `T-XX` <!-- ej: T-06 --> |
| **Rol Responsable** | <!-- AI Engineer / Backend / Frontend / Cloud OCI / QA --> |
| **Estado del PR** | `status: in-review` ➔ `status: done` (al mergear) |

---

## 📝 Descripción del Cambio

<!-- Explicación concisa de la solución técnica implementada y decisiones clave tomadas -->

---

## 🛠️ Cambios Realizados

- <!-- Archivo creado o modificado 1 -->
- <!-- Archivo creado o modificado 2 -->
- <!-- Lógica o configuración añadida -->

---

## ✅ Criterios de Aceptación Cumplidos

<!-- Copiar los criterios del Issue original marcados como completados -->
- [ ] <!-- Criterio 1 -->
- [ ] <!-- Criterio 2 -->
- [ ] <!-- Criterio 3 -->

---

## 🔬 Validación y Pruebas

- [ ] **Validación SDD:** La salida producida cumple 100% con los esquemas en `schemas/`.
- [ ] **Caso Clínico Probado:** Probado con dataset: `datasets/<!-- caso_1 / caso_2 / caso_3 -->.json`.

---

## 📸 Evidencia Visual / Logs (Si aplica)

| Captura de UI / Workflow n8n | Log de Ejecución / Payload JSON |
|---|---|
| <!-- ![Captura](url) --> | <!-- ```json ... ``` --> |

---

## 📋 Checklist del Autor para Pasar a Revisión

- [ ] He vinculado el issue correspondiente con `Closes #XX`.
- [ ] En la barra lateral derecha 👉 verifiqué que el PR esté asignado al **GitHub Project** del equipo.
- [ ] Mi código sigue las convenciones del proyecto y la metodología SDD.
- [ ] **Sin credenciales expuestas:** No hay API keys ni secretos en el código (se usa `.env`).
- [ ] Los commits siguen el formato **Conventional Commits** (`feat(T-XX): ...`).
- [ ] El branch está actualizado con `main` (`git merge main` ejecutado sin conflictos).
- [ ] Las pruebas locales corren sin errores.
