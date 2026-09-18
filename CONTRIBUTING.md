# 🩺 Guía de Contribución – MediFlow

¡Bienvenidos al proyecto **MediFlow** para la Hackathon ONE G10!

Para mantener un estándar de ingeniería de software riguroso y transparente, seguimos la metodología **Schema-Driven Development (SDD)**.

---

## 📌 Reglas de Oro para Contribuir

1. **Lee primero el SDD:** Todo el diseño del sistema está documentado en [`docs/sdd.md`](docs/sdd.md).
2. **Respeta los Contratos de Datos:** Ningún módulo debe enviar o recibir datos que no validen contra los esquemas en [`schemas/`](schemas/).
3. **Usa Conventional Commits:** Los commits deben usar el estándar `tipo(scope): mensaje` (ej. `feat(T-06): prompt de extraccion multimodal`).
4. **Consulta la Guía de Desarrollo:** En [`docs/guia-desarrollo.md`](docs/guia-desarrollo.md) tienes fragmentos de código listos (*snippets*) para cada tarea.
5. **Verifica el Backlog:** Las tareas se toman del archivo [`docs/backlog.md`](docs/backlog.md).
6. **No expongas credenciales:** Utiliza siempre variables de entorno referenciadas en `.env.example`.

Para consultar la guía completa de commits, versionamiento semántico (SemVer) y la definición de terminado (Definition of Done), revisa [`docs/workflow.md`](docs/workflow.md).
