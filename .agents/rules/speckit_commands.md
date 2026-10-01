---
trigger: always_on
description: Soporte y ejecución de comandos Slash de Spec Kit en el chat de Antigravity
---

# Comandos de Spec Kit en el Chat de Antigravity

Cuando el usuario escriba comandos con prefijo `/` o comandos directos de Spec Kit en este chat, el agente debe reconocerlos inmediatamente y ejecutar el flujo correspondiente leyendo la skill de `.agents/skills/`:

| Comando en Chat | Skill / Flujo a Ejecutar | Ubicación de Instrucciones |
|---|---|---|
| `/speckit-specify [descripción]` o `/specify [descripción]` | **speckit-specify**: Crea la especificación funcional y requisitos en `specs/` | `.agents/skills/speckit-specify/SKILL.md` |
| `/speckit-plan` o `/plan-spec` | **speckit-plan**: Diseña la arquitectura, dependencias y plan técnico | `.agents/skills/speckit-plan/SKILL.md` |
| `/speckit-tasks` o `/tasks` | **speckit-tasks**: Desglosa las tareas ejecutables guiadas por TDD | `.agents/skills/speckit-tasks/SKILL.md` |
| `/speckit-implement` o `/implement` | **speckit-implement**: Ejecuta la implementación paso a paso pasando tests en verde | `.agents/skills/speckit-implement/SKILL.md` |
| `/speckit-clarify` o `/clarify` | **speckit-clarify**: Formula preguntas clave para resolver ambigüedades | `.agents/skills/speckit-clarify/SKILL.md` |
| `/speckit-analyze` | **speckit-analyze**: Analiza consistencia entre especificaciones y código | `.agents/skills/speckit-analyze/SKILL.md` |
| `/speckit-checklist` | **speckit-checklist**: Genera lista de verificación de calidad | `.agents/skills/speckit-checklist/SKILL.md` |
| `/speckit-constitution` | **speckit-constitution**: Administra la constitución del proyecto | `.agents/skills/speckit-constitution/SKILL.md` |

Al recibir cualquiera de estos comandos:
1. Cargar y leer el archivo `SKILL.md` correspondiente usando `view_file`.
2. Seguir rigurosamente sus instrucciones y plantillas en `.specify/`.
3. Informar al usuario del progreso en cada fase.
