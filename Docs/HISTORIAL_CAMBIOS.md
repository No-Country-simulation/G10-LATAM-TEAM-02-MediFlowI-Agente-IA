# 📜 Índice General de Historiales de Cambios — MediFlow

Este documento es el **índice maestro** de los registros de cambios del proyecto **MediFlow (Agente Autónomo de Triaje Clínico Multimodal)**. Todos los historiales individuales se almacenan en la subcarpeta `Docs/historial_cambios/` bajo la nomenclatura incremental `HISTORIAL_CAMBIOS_AAAA-MM-DD_CAMBIO[N].md`, lo que permite registrar múltiples sesiones de cambio en un mismo día (`CAMBIO1`, `CAMBIO2`, etc.).

---

## 📅 Registros de Cambios por Fecha e Identificador

| Fecha | Identificador | Autor | Título del Registro | Enlace al Documento |
| :--- | :--- | :--- | :--- | :--- |
| **14/09/2026** | `CAMBIO1` | Todos | Sprint 1 — Arquitectura Base & Setup Inicial | [HISTORIAL_CAMBIOS_2026-09-14_CAMBIO1.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-14_CAMBIO1.md) |
| **24/09/2026** | `CAMBIO1` | Erick Pariona | Sprint 2 — Control Manual Almacenamiento, Comentarios BD, Aislar Pruebas & UX Polish | [HISTORIAL_CAMBIOS_2026-09-24_CAMBIO1.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-24_CAMBIO1.md) |
| **25/09/2026** | `CAMBIO1` | Erick Pariona | Reorganización de Docs en subcarpetas e independización de historiales incrementales | [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO1.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO1.md) |
| **25/09/2026** | `CAMBIO2` | Erick Pariona | Módulo 1 — Autenticación (DNI 8 cifras), Usuarios & Control de Acceso RBAC (RF-01 a RF-05) | [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO2.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO2.md) |
| **25/09/2026** | `CAMBIO3` | Antigravity & Erick Pariona | Refactor de esquemas Pydantic v2 y eliminación de advertencias en Backend | [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO3.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO3.md) |
| **25/09/2026** | `CAMBIO4` | Antigravity & Erick Pariona | Acoplamiento de `mediflow-frontend` manteniendo intacta la Consola de Triaje & Usuarios | [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO4.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO4.md) |
| **25/09/2026** | `CAMBIO5` | Antigravity & Erick Pariona | Rediseño UX/UI de Configuración de Almacenamiento y Pestañas de Navegación | [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO5.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO5.md) |
| **25/09/2026** | `CAMBIO6` | Antigravity & Erick Pariona | Rediseño UX/UI del Formulario de Registro de Usuarios y Tabla RBAC | [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO6.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO6.md) |
| **25/09/2026** | `CAMBIO7` | Antigravity & Erick Pariona | Rediseño visual de Consola de Triaje Clínico y Maquetación Responsiva en MainLayout | [HISTORIAL_CAMBIOS_2026-09-25_CAMBIO7.md](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/historial_cambios/HISTORIAL_CAMBIOS_2026-09-25_CAMBIO7.md) |

---

## ⚡ Nomenclatura y Automatización de Registros de Cambio

La regla de nomenclatura para los archivos de historial de cambios en la carpeta `Docs/historial_cambios/` es:
> `Docs/historial_cambios/HISTORIAL_CAMBIOS_AAAA-MM-DD_CAMBIO[N].md`

Donde:
- `AAAA-MM-DD` es la fecha del sistema tomada automáticamente.
- `CAMBIO[N]` es el identificador correlativo (`CAMBIO1`, `CAMBIO2`, `CAMBIO3`, etc.).

Para solicitar un nuevo registro de cambios al Agente IA:
> *"genera historial cambios para autor [Nombre]"*

El Agente IA tomará la fecha actual, detectará la secuencia del día, creará el archivo `Docs/historial_cambios/HISTORIAL_CAMBIOS_AAAA-MM-DD_CAMBIO[N].md` usando [`Docs/PLANTILLA_CAMBIOS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/PLANTILLA_CAMBIOS.md) y actualizará este índice maestro [`Docs/HISTORIAL_CAMBIOS.md`](file:///c:/proyectos_git_parionayauricasa/G10-LATAM-TEAM-02-MediFlowI-Agente-IA/Docs/HISTORIAL_CAMBIOS.md).
