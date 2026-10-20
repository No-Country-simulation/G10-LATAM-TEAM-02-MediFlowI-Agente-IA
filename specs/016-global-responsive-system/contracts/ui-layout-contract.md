# UI Layout Contract: Especificación de Layout y Breakpoints Responsivos

**Feature**: `016-global-responsive-system`  
**Date**: 2026-10-20  

---

## 1. Puntos de Interrupción (Breakpoints)

| Token | Rango de Ancho | Caso de Uso Primario | Comportamiento del Layout |
|---|---|---|---|
| `base` / `xs` | `< 640px` | Móviles clínicos (360px - 480px) | Sidebar en drawer oculto; KPIs 1 columna; Tablas con scroll horizontal y paginación apilada |
| `sm` | `≥ 640px` | Móviles horizontales / phablets | Sidebar en drawer; KPIs 2 columnas; Controles de filtro en 2 columnas |
| `md` | `≥ 768px` | Tablets en orientación vertical | Sidebar en drawer; Paginación en 1 fila; Filtros en cuadrícula compacta |
| `lg` | `≥ 1024px` | Laptops y Tablets apaisadas | Sidebar fijo a la izquierda (`w-64`); KPIs 4 columnas; Botón de hamburguesa oculto |
| `xl` | `≥ 1280px` | Monitores clínicos de escritorio | Vista dividida paralela (Visor + Ficha IA); Tablas con visualización holgada |
| `2xl` | `≥ 1536px` | Pantallas de alta densidad | Contenedor centrado con `max-w-7xl` para ergonomía visual |

---

## 2. Contrato de Componente: Shell Principal (`MainLayout`)

### Propiedades y Estado
- `isMobileSidebarOpen: boolean` (Controla apertura del drawer en `< 1024px`)
- `toggleMobileSidebar: () => void`
- `closeMobileSidebar: () => void`

### Estructura de Renderizado
```tsx
<div className="min-h-screen bg-slate-50 flex flex-col lg:flex-row overflow-x-hidden">
  {/* Cabecera Móvil solo visible en < 1024px */}
  <header className="lg:hidden flex items-center justify-between px-4 py-3 bg-white border-b border-slate-200 sticky top-0 z-40">
    <button onClick={toggleMobileSidebar} aria-label="Abrir menú de navegación" className="p-2 text-slate-700 hover:bg-slate-100 rounded-lg">
      <FaBars size={20} />
    </button>
    <div className="font-bold text-slate-900">MediFlow</div>
    <div className="w-8" /> {/* Espaciador balanceado */}
  </header>

  {/* Backdrop en móvil */}
  {isMobileSidebarOpen && (
    <div className="fixed inset-0 bg-slate-900/50 backdrop-blur-sm z-40 lg:hidden" onClick={closeMobileSidebar} />
  )}

  {/* Sidebar (fijo en lg, drawer en < lg) */}
  <aside className={`fixed inset-y-0 left-0 z-50 w-64 bg-slate-900 text-white transform transition-transform duration-300 ease-in-out lg:translate-x-0 ${isMobileSidebarOpen ? 'translate-x-0' : '-translate-x-full'}`}>
    {/* Contenido Sidebar con botón de cierre móvil */}
  </aside>

  {/* Área de contenido principal */}
  <main className="flex-1 lg:pl-64 min-w-0 overflow-y-auto">
    <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
      {/* Outlet de vistas */}
    </div>
  </main>
</div>
```

---

## 3. Contrato de Componente: Contenedor de Tabla Clínica (`DocumentTable`)

### Reglas de Presentación
1. Contenedor padre inmediato: `w-full max-w-full overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm`.
2. Tabla: `min-w-[800px] w-full text-left`.
3. Pie de Paginación:
   ```tsx
   <div className="flex flex-col sm:flex-row items-center justify-between gap-3 px-4 py-3 border-t border-slate-200 bg-slate-50/50">
     {/* Resumen registros */}
     <div className="text-xs sm:text-sm text-slate-600 text-center sm:text-left">
       Mostrando 1 a 10 de 50 documentos
     </div>
     {/* Botones de paginación */}
     <div className="flex items-center gap-1.5 flex-wrap justify-center">
       {/* Anterior, Páginas, Siguiente */}
     </div>
   </div>
   ```

---

## 4. Contrato de Notificación Flotante (`EmergencyAlertToast`)

### Anclaje y Dimensiones
- Móvil (`< 640px`): `top-4 inset-x-4 max-w-none rounded-xl shadow-2xl`
- Escritorio (`≥ 640px`): `top-4 right-4 w-96 max-w-[calc(100vw-2rem)]`
- Z-Index: `z-50` para mantenerse por encima del contenido y diálogos sin colisionar con el backdrop.
