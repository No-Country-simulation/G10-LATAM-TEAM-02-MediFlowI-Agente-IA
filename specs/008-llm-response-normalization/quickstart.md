# Quickstart: Validación de Normalización de Respuestas LLM

Este documento describe cómo verificar la correcta normalización y deserialización de respuestas del LLM tanto de forma automatizada como end-to-end.

## 1. Verificación Automatizada (TDD)

Ejecutar las pruebas unitarias creadas para validar la deserialización multiformato:

```bash
cd backend
.venv/bin/pytest tests/test_llm_service.py -v
```

Ejecutar la suite completa de pruebas para garantizar cero regresiones:

```bash
cd backend
.venv/bin/pytest tests/ -v
```

## 2. Verificación End-to-End con el Documento de Prueba

Procesar nuevamente el documento clínico `caso_3_medicina_amigdalitis.pdf` a través de la API o la interfaz gráfica:

1. Abrir la interfaz en [http://localhost:5173](http://localhost:5173).
2. Subir el archivo `caso_3_medicina_amigdalitis.pdf` en la Consola de Triaje.
3. Comprobar que en la pantalla de resultados:
   - **Paciente**: Mateo Daniel Torres Salazar (DNI: 44332211, HC: 12890, Edad: 19 años).
   - **Diagnóstico**: Faringoamigdalitis aguda (o equivalente detectado).
   - **CIE-10**: J03 o J03.9 sugerido y validado.
   - **Score de Confianza**: > 80%.
   - **Destino**: `Consulta Externa` / `Medicina General`.
