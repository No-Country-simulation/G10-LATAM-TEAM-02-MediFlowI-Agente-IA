# MediFlow – Sistema de Diseño & Guía de Estilos UI

Documentación oficial de los tokens visuales, escala tipográfica y sistema de color para **MediFlow: Sistema Autónomo de Triaje y Enrutamiento Clínico**.

[Enlace del diseño en Figma](https://www.figma.com/design/gnxgEUbrYMioeIwrMrhaKe/MediFlow?node-id=62-3453&t=vxhO7ufUI9nwLB2q-0)

---

## 1. Paleta Clínica de Severidad y Estados Médicos

Paleta semántica estandarizada para clasificar la urgencia clínica de las solicitudes, priorización en el enrutamiento y estado de los registros:

| Nivel / Estado | Hex | Muestra | Uso en MediFlow |
| :--- | :--- | :---: | :--- |
| **Emergencia** | `#EF4444` | 🔴 | **Prioridad Crítica / Alerta:** Casos de riesgo vital inmediato, errores críticos del sistema y solicitudes rechazadas. |
| **Urgente** | `#F59E0B` | 🟡 | **Atención Prioritaria / Pendiente:** Solicitudes en espera de validación, triaje que requiere atención pronta sin paro inminente. |
| **Rutina** | `#10B981` | 🟢 | **Atención Regular / Aceptada:** Flujo estándar, signos vitales estables, solicitudes aprobadas y usuarios activos. |
| **Auditoría** | `#3B82F6` | 🔵 | **Trazabilidad y Revisión:** Auditoría de autorizaciones, expedientes en supervisión médica y notas de enrutamiento. |

---

## 2. Paleta de Colores UI & Marca (Brand Colors)

Tokens de interfaz para la navegación, superficies, formularios e interactividad:

### Colores Principales
* **Primary Blue (`#2C5282`):** Color de marca principal. Utilizado en botones de acción principal (CTA como *Iniciar sesión*, *Enviar solicitud*), encabezados principales y estados seleccionados en menús desplegables.
* **Secondary Teal/Green (`#6FCF97`):** Color secundario de soporte positivo, acentos en isotipo de MediFlow y confirmaciones de éxito.
* **Tertiary Soft Purple (`#BC9CFF`):** Acento visual complementario y transiciones cromáticas en fondos/degradados.

### Feedback y Validación de Formularios
* **Error / Alerta (`#F72C2C` / `#EF4444`):** Bordes activos de inputs con error (`Ej. "Por favor, introduzca una dirección de correo electrónico válida"`), textos de advertencia y botones de rechazo.
* **Success (`#10B981`):** Indicadores de éxito y badges de estatus aprobado (*Aceptada*).
* **Warning (`#F59E0B`):** Badges de estado en espera (*Pendiente*).

### Escala de Neutros y Sombras (Dark Shades)
* **Dark Shade 100% (`#1F2041`):** Color estructural para tipografía de alta jerarquía, títulos principales y panel lateral oscuro (testimonios del login).
* **Dark Shade 75% (`#1F2041` al 75%):** Texto de lectura regular, etiquetas de formularios y nombres de usuario en tablas.
* **Dark Shade 50% (`#1F2041` al 50%):** Iconos secundarios, placeholders y descripciones auxiliares.
* **Dark Shade 25% (`#1F2041` al 25%):** Bordes de inputs inactivos, divisores de tablas y bordes de selectores.
* **Dark Shade 5% / Surface (`#1F2041` al 5% o `#F8FAFC`):** Fondos de tarjetas principales, contenedores de tablas y modales.

---

## 3. Jerarquía Tipográfica

Estructura de fuentes y tamaños para optimizar la legibilidad en pantallas de administración y triaje:

* **H1 / Display:** Título de bienvenida o pantalla principal (`"Solicitudes de acceso"`, `"Bienvenido a MediFlow"`). Peso: Bold / SemiBold.
* **H2:** Títulos de vista intermedia y secciones principales del módulo (`"Bienvenido"`, `"Crea tu cuenta"`).
* **H3:** Encabezados de widgets, módulos secundarios o tablas de datos.
* **H4:** Subtítulos de contexto o nombres de campos destacados (`"Usuarios"`, `"Rol / Departamento"`, `"Estado de la solicitud"`).
* **H5 / Body:** Texto corrido, registros de tabla, e-mails, citas de usuario y descripciones explicativas.
* **H6 / Overline & Badges:** Micro-copy en mayúsculas (`"SISTEMA AUTÓNOMO DE TRIAJE Y ENRUTAMIENTO CLÍNICO"`, `"CORREO"`, `"CONTRASEÑA"`) y etiquetas compactas de estado (*Aceptada*, *Rechazada*, *Pendiente*).

---

## 4. Componentes Clave Documentados

* **Badges de Estado:** Contenedores tipo píldora con indicador circular para seguimiento de solicitudes (`Aceptada`, `Pendiente`, `Rechazada`).
* **Inputs y Validaciones:** Estados por defecto, en foco, con error (borde rojo y helper text explicativo) y estado de carga (loader/spinner en botón).
* **Selectores de Departamento:** Menús de selección rápida para departamentos clínicos (`Urgencias Médicas`, `Auditoría de Autorizaciones`, `Farmacia Hospitalaria`, `Revisión Humana`, `Historia Clínica Electrónica`).