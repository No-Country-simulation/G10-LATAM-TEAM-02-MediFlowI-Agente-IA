# Quickstart: Guía de Validación y Ejecución de Visor Clínico WebP

**Feature**: `012-webp-clinical-viewer`  
**Date**: 2026-10-17  
**Status**: Completed  

---

## 1. Prerrequisitos

- Node.js instalado (v18+).
- Dependencias de `frontend` instaladas (`npm install` ejecutado).

---

## 2. Ejecución de Pruebas Automatizadas

Para validar unitariamente el funcionamiento de la carga y visualización de archivos WebP:

```bash
# Ejecutar la suite unitaria de DocumentViewer
npx vitest run src/tests/components/documents/DocumentViewer.test.tsx

# Ejecutar verificación de tipos y compilación limpia
npm run build
```

**Resultado esperado**:
- Todos los tests de `DocumentViewer.test.tsx` pasan al 100% en verde.
- `tsc -b && vite build` compila con 0 errores y 0 advertencias de TypeScript.

---

## 3. Escenarios de Validación Manual en la Aplicación

### Escenario 1: Selección y Carga de Archivo WebP en `DocumentUploader`
1. Iniciar la aplicación: `npm run dev` en `frontend`.
2. Navegar a la pantalla de nuevo documento (`/documentos/nuevo`).
3. Arrastrar o seleccionar un archivo de prueba con extensión `.webp` (tamaño < 10 MB).
4. **Verificación**: El dropzone cambia a estado verde ("border-success"), se muestra el nombre del archivo, su tamaño formateado, y no aparece ninguna alerta de formato inválido.

### Escenario 2: Visualización de Imagen WebP con Controles de Zoom en `DocumentViewer`
1. Abrir un documento clínico con URL `.webp` en la vista de detalle de documento o triaje.
2. **Verificación**: La imagen se visualiza nítida y ajustada al marco sin desbordar el contenedor.
3. Presionar el botón `+` de zoom: la imagen aumenta un 25% con transiciones fluidas.
4. Presionar el botón `-` de zoom: la imagen se reduce.
5. Presionar el botón `100%`: la escala vuelve a la dimensión original contenida.
6. Presionar el botón de pantalla completa: el contenedor se expande para ocupar la ventana completa.

### Escenario 3: Manejo de Error ante Archivo WebP Corrupto o Dañado
1. Proveer a `DocumentViewer` una URL que apunte a un recurso inexistente o con contenido binario corrupto que el navegador no pueda decodificar.
2. **Verificación**: El visor detecta el evento de error, oculta el icono roto por defecto del navegador y muestra una alerta médica con el mensaje:
   *"No fue posible decodificar o cargar la imagen clínica. El archivo podría estar dañado o el formato no es compatible con el navegador."*
3. Se provee un botón para abrir el enlace original en una pestaña independiente.

