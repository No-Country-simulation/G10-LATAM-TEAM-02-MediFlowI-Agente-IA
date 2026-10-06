# Catálogo CIE-10 para MediFlow

`cie10_catalog.json` contiene 11.008 códigos únicos y sus descripciones en español.
Se obtuvo del archivo `cie10_master.json` proporcionado por el responsable de la
tarea en su directorio `CIE-10`, generado previamente a partir de `CIE-10.pdf`.
Se conservaron literalmente los códigos y descripciones; únicamente se transformó
la lista en un índice JSON de código a descripción.

Huellas SHA-256 de las fuentes proporcionadas:

- JSON: `5ac8d47a4c27b68ede88a5b82f97b67a71ba67e2fe74b4ed37c51f08fa73ff1b`
- PDF: `07acd64eff54018522af5cbd656732348baa534a17b7eb93e8aab2650cfd40b8`

El índice incluye categorías de tres caracteres y subcategorías de cuatro
caracteres. La normalización admite minúsculas, espacios en los extremos y
ausencia de punto decimal: `i219` pasa a `I21.9`. No se corrigen otros errores ni
se sustituyen códigos desconocidos por una categoría más general.

La prioridad sugerida del JSON original no forma parte de este índice ni modifica
el enrutamiento. La validación verifica pertenencia al catálogo, no correspondencia
del código con el diagnóstico del paciente. `cie10_descripcion` conserva la etiqueta
del catálogo separada de `diagnostico_principal`.

Un código inválido sugerido durante la extracción se elimina de los datos clínicos,
se conserva en `metadata.cie10_codigos_invalidos` para trazabilidad y obliga a
auditoría humana. La ausencia de código no obliga a auditoría por sí sola.

PostgreSQL sigue almacenando el código canónico. La descripción de las consultas
se obtiene de ese código y este índice, incluyendo códigos corregidos por HITL;
no se añade una columna redundante ni se requiere una migración.

Para actualizar el catálogo, sustituir el índice desde una fuente clínica aprobada,
documentar su procedencia y huellas, y ejecutar las pruebas CIE-10 y la suite completa.
