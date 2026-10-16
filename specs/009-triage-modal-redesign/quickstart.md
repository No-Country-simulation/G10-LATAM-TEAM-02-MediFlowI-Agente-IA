# Quickstart & Verification Guide: Rediseño del Modal de Triaje y Píldoras RBAC

**Feature**: `009-triage-modal-redesign`
**Date**: 2026-10-13
**Status**: Ready for Implementation

---

## 1. Prerrequisitos

- Entorno de frontend con Node.js y dependencias instaladas en `frontend/`.
- Backend de MediFlow activo o servidor de desarrollo frontend:
  ```bash
  cd frontend
  npm run dev
  ```

---

## 2. Escenarios de Validación Manual

### Escenario 1: Control de Acceso RBAC en Píldoras Superiores
1. Iniciar sesión con un usuario con rol `ADMINISTRADOR`:
   - Ir a `/triaje`.
   - **Resultado esperado**: La cápsula superior muestra **3 opciones**: `Enrutamiento` (activa), `Historial` y `Solicitudes`.
   - Hacer clic en `Historial` ➔ Navega a `/documentos`.
   - Regresar a `/triaje` y hacer clic en `Solicitudes` ➔ Navega a `/auditoria`.
2. Iniciar sesión con un usuario con rol `OPERADOR` o `AUDITOR`:
   - Ir a `/triaje`.
   - **Resultado esperado**: La cápsula superior muestra únicamente **2 opciones**: `Enrutamiento` e `Historial`. La opción `Solicitudes` no es visible.

### Escenario 2: Aspecto Visual del Modal y Dropzone (Imagen 1)
1. En `/triaje`, verificar la presentación inicial:
   - Título centrado grande `Buen día [Dr. Nombre/Lucas]`.
   - Subtítulo descriptivo centrado.
   - Píldora del modelo IA (`GPT-5.2` con fondo verde secundario) e icono FontAwesome de sliders a la derecha.
   - Tarjeta central blanca con bordes curvados (`rounded-3xl`) y sombra suave.
   - Título `Ejecutar nuevo análisis` y subtítulo de formatos soportados (`PDF, PNG, JPG, JPEG, JSON (Máx. 10 MB)`).
   - Zona de arrastre con borde discontinuo, icono FontAwesome `faFolder`, texto y botón azul marino `Seleccionar archivos` (`--primary`).
   - Selector dropdown de `Canal de Origen` visible y operativo.

### Escenario 3: Archivo Cargado / Seleccionado (Imagen 2)
1. Seleccionar o arrastrar un archivo PDF (ej. `Client agreement template.pdf`):
   - **Resultado esperado**: La dropzone cambia inmediatamente a una fila redondeada con fondo suave `bg-slate-100`.
   - Muestra icono FontAwesome `faPaperclip`, nombre del archivo, tamaño en MB (ej. `4.6 MB`) e icono de acción.
   - Abajo a la derecha aparecen los botones `Cancelar` y `Continuar`.
2. Hacer clic en `Cancelar`:
   - **Resultado esperado**: El archivo se descarta y el modal vuelve al estado de dropzone vacía.

### Escenario 4: Procesamiento con Loader Circular (Imagen 3)
1. Seleccionar un archivo y presionar `Continuar`:
   - **Resultado esperado**: La fila del archivo muestra porcentaje y spinner circular animado de FontAwesome (`faSpinner` / `faCircleNotch`), y los botones se deshabilitan durante la llamada a la API.
   - Al responder el backend, se muestra el diagnóstico correspondiente.

---

## 3. Comandos Automatizados de Verificación (Gates Obligatorios)

```bash
# 1. Verificación de tipos TypeScript y empaquetado de producción
cd frontend
npm run build

# 2. Ejecución de la suite completa de pruebas unitarias
npm run test
```

Ambos comandos deben concluir con 0 errores y 100% de pruebas en verde antes de dar por finalizada la implementación.

