# Research & Technical Decisions: Sistema Global Responsive

**Feature**: `016-global-responsive-system`  
**Date**: 2026-10-20  
**Status**: Completed  

---

## Decisiones Técnicas Clave

### 1. Estrategia de Breakpoints y Rejilla con Tailwind CSS
- **Decisión**: Utilizar la escala de breakpoints estándar de Tailwind CSS enriquecida con tokens de diseño clínico:
  - `sm`: 640px (Móviles grandes en horizontal / Phablets)
  - `md`: 768px (Tablets retrato / iPad clínico)
  - `lg`: 1024px (Laptops de guardia / Tablets apaisadas)
  - `xl`: 1280px (Monitores estándar hospitalarios)
  - `2xl`: 1536px (Monitores panorámicos de alta resolución)
- **Razón**: Permite componer layouts móviles primero (*mobile-first*) con utilidades nativas (`hidden md:flex`, `grid-cols-1 sm:grid-cols-2 lg:grid-cols-4`, `w-full lg:w-auto`).
- **Alternativas descartadas**: 
  - CSS media queries ad-hoc en archivos CSS separados (rechazado por violar la Constitución MediFlow que exige Tailwind CSS).
  - Frameworks auxiliares como Bootstrap Grid (genera conflictos de clases con Tailwind y duplica el bundle).

### 2. Navegación Principal y Shell (`Sidebar` & `MainLayout`)
- **Decisión**: Implementar un patrón híbrido:
  - En pantallas grandes (`lg:` ≥ 1024px): Barra lateral estática visible a la izquierda con ancho fijo (`w-64` / 256px) y contenido con margen dinámico (`lg:pl-64`).
  - En pantallas compactas (`< 1024px`): Barra lateral oculta por defecto (`-translate-x-full lg:translate-x-0`), transformable en panel deslizante (*drawer*) al accionar el botón de menú hamburguesa ubicado en una cabecera móvil persistente (`MobileNavbar`). Incluye un fondo oscuro con desenfoque (*backdrop-blur-sm*) para cerrar con un toque.
- **Razón**: Resuelve de raíz el principal bug de superposición donde el sidebar pisaba el contenido o generaba barras de scroll horizontal descontroladas.
- **Alternativas descartadas**:
  - Menú inferior de pestañas (Bottom Navigation Bar): Descartado porque MediFlow cuenta con 9+ rutas y selectores de rol que requieren jerarquía vertical.

### 3. Tablas de Datos Clínicos de Alta Densidad
- **Decisión**:
  - Contenedor con aislamiento de desbordamiento: Todo componente de tabla (`DocumentTable`, vistas de Pacientes y Usuarios) se encapsula en `<div className="overflow-x-auto w-full max-w-full">` con bordes suaves que señalan la continuación de datos.
  - Paginación apilable: La barra inferior de paginación usa `flex flex-col sm:flex-row items-center justify-between gap-3` asegurando que en móviles el resumen de registros quede centrado arriba y los botones de acción Anterior/Siguiente no se salgan de pantalla.
  - Dimensiones táctiles: Botones de fila con altura mínima táctil de 40px (`min-h-[40px] px-3.5`).
- **Razón**: Permite a los médicos acceder a la totalidad de las 10 columnas clínicas en tablet o teléfono mediante deslizamiento natural sin romper el layout exterior de la página.

### 4. Parrillas Bento y Paneles KPI
- **Decisión**: Migrar clases fijas de Bootstrap (`row`, `col-12 col-sm-6 col-xl-3`) a clases utilitarias de Tailwind Grid:
  - `grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4`
- **Razón**: Distribución geométrica perfecta sin márgenes negativos de Bootstrap (`gx`, `gy`) que son la causa frecuente de desbordamiento horizontal (`overflow-x`) en pantallas pequeñas.

### 5. Visor Documental y Ficha de Triaje Dividida
- **Decisión**: Reorganizar la vista dividida en `/documentos/:id` y `/auditoria/:id` usando un layout flex/grid adaptable:
  - Desktop (`≥ 1200px`): 2 columnas paralelas (`grid grid-cols-12 gap-6`, 7 cols visor + 5 cols datos).
  - Tablet/Mobile (`< 1200px`): Modo apilado vertical o pestañas selectoras tipo `SegmentedControl` ("Visor Documental" / "Ficha Clínica").
- **Razón**: Evita que en pantallas de 768px el visor y el formulario se reduzcan a franjas ilegibles de 300px de ancho cada una.

### 6. Modales y Diálogos de Captura
- **Decisión**: Establecer clases universales de diálogo clínico:
  - Contenedor: `w-full max-w-lg md:max-w-2xl lg:max-w-4xl mx-auto my-6 max-h-[90vh] flex flex-col`
  - Encabezado y pie fijos: `flex-shrink-0`
  - Cuerpo desplazable: `flex-1 overflow-y-auto p-4 sm:p-6`
- **Razón**: Tolera la apertura de teclados virtuales en dispositivos táctiles sin cortar los botones "Guardar" o "Cancelar".
