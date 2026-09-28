# US-01: contrato OpenAPI y generación de tipos

## Qué hace cada pieza

`specs/openapi.yaml` es la entrada del contrato. Las rutas están en `specs/paths/` y los modelos en `specs/components/schemas.yaml`. Estos archivos definen la comunicación HTTP; PostgreSQL sigue siendo la fuente de verdad de los datos persistidos.

- `make validate`: reúne las referencias en un JSON temporal y ejecuta Spectral con `.spectral.yaml`.
- `make generate`: valida ese mismo contrato y genera Pydantic v2 y TypeScript. Si una herramienta falla, devuelve error y conserva las salidas anteriores. No considera esos archivos una generación exitosa.
- `make generate-check`: vuelve a generar en una carpeta temporal y comprueba que los archivos versionados coincidan. No modifica el repositorio.

El bundle temporal resuelve una incompatibilidad reproducida de Spectral 6.15.0 con referencias externas de Path Items en OpenAPI 3.1 y permite a datamodel-code-generator 0.35.0 procesar los schemas. No elimina componentes ni desactiva la validación estructural.

## Preparación (una vez por entorno)

Requisitos: Python 3.11 o superior, Node.js 22 o superior y GNU Make si quieres usar los comandos `make`.

Desde la raíz del repositorio, con tu entorno virtual activo:

```powershell
python -m pip install -e "./backend[dev,sdd]"
npm ci
```

Las herramientas Node del contrato se instalan en la raíz, separadas del frontend. `package.json` fija sus versiones y `package-lock.json` fija el árbol de dependencias. El extra Python `sdd` fija datamodel-code-generator y sus formateadores.

El Makefile usa `.venv/Scripts/python.exe` en Windows o `.venv/bin/python` en Unix si existen. También puedes indicar `make PYTHON=ruta/al/python generate`. Node debe estar en PATH; un entorno con Node en otra ubicación puede definir `NODE_BINARY` con la ruta del ejecutable.

Si no tienes Make, los comandos equivalentes son:

```powershell
python infrastructure/scripts/validate_spec.py
python infrastructure/scripts/generate.py
python infrastructure/scripts/generate.py --check
```

Ningún comando instala herramientas silenciosamente. Si falta alguna dependencia, corrige el entorno y repite el comando.

## Flujo de trabajo

1. Edita el YAML de la ruta o del schema correspondiente.
2. Ejecuta `make validate`.
3. Ejecuta `make generate`.
4. Revisa el diff y ejecuta las pruebas y el build.
5. Incluye el contrato y sus salidas generadas en el mismo cambio.

Ejemplo: si agregas un campo opcional `observacion` a un schema, la siguiente generación lo agrega a Python y TypeScript. No escribas el campo a mano en las carpetas `_generated/`.

Pydantic valida datos en ejecución cuando se usa el modelo. TypeScript comprueba tipos al compilar; por sí solo no valida el JSON recibido por HTTP. Spectral revisa el contrato, no ejecuta los endpoints.

## Salidas e integración

- `backend/app/_generated/models.py`: modelos Pydantic generados. El modelo de entrada se llama `DocumentoClinico`, igual que en el contrato. El endpoint lo importa con el alias local `DocumentoClinicoRequest` para conservar su nombre interno.
- `frontend/src/_generated/api/types.ts`: schemas y tipos de operaciones HTTP generados por openapi-typescript.
- `frontend/src/_generated/api/index.ts`: alias de importación generados automáticamente a partir de los nombres de schemas.
- `frontend/src/api/triage.api.ts`: mantiene las funciones HTTP manuales y consume los tipos generados. Ejemplo: `import type { ResultadoTriaje } from '../_generated/api'`.
- `AgentState` permanece en `backend/app/agent/state.py`. Es estado interno del grafo y no se genera desde OpenAPI.

`PrioridadTriaje` se reutiliza mediante referencias. En Pydantic es un RootModel; al serializar produce el valor de texto normal, por ejemplo `Urgente`.

## Decisiones de compatibilidad

- `canal_origen` es opcional con valor por defecto vacío porque ese es el comportamiento vigente de `/triage`. Incluirlo con `null` es inválido. Hacerlo obligatorio sería un cambio de API, no una reparación del generador.
- Los campos que admiten `null` usan `type: [string, 'null']` o `anyOf`, según corresponda a OpenAPI 3.1.
- `tipo_documento` conserva el catálogo clínico y documenta tres valores ya emitidos por el código: `Desconocido`, `Error` y `Documento Clínico`. No acepta texto arbitrario como `FACTURA`.
- Los errores describen el envoltorio `detail` que devuelve FastAPI. El 422 tiene su propio schema de validación. No se cambió el manejador de errores.
- `EntidadesMedicas` es un modelo independiente reservado; todavía no forma parte de las respuestas del agente. Spectral informa una advertencia por ese componente sin uso. Se mantiene visible porque US-01 pide modelarlo; no se agregó extracción clínica nueva para ocultar la advertencia.
- El ejemplo `backend/probando_modelos.py` serializa las entidades por separado y comprueba su lectura posterior, sin enviarlas a un campo inexistente.

## Verificación

```powershell
make validate
make generate
make generate-check
cd backend
python -m pytest tests/ -q
python probando_modelos.py
cd ../frontend
npm run build
```

Las pruebas de SDD verifican generación desde cero, reproducibilidad, propagación de cambios a ambos lenguajes, rechazo de contratos inválidos y conservación de salidas cuando falla una herramienta. Las pruebas de contrato comparan respuestas del API con JSON Schema usando datos sintéticos y dependencias simuladas.

Pytest fuerza DATABASE_URL vacío y archivos temporales para evitar escrituras en mediflow_dev y en el almacenamiento del usuario. Las pruebas de migraciones generan SQL con `alembic upgrade head --sql` y una URL ficticia; no establecen una conexión.

Para comprobar las migraciones de la base real, configura DATABASE_URL en `backend/.env` y ejecuta Alembic desde `backend`. La verificación SQL offline no demuestra que mediflow_dev esté sincronizada. No se requieren migraciones nuevas para US-01.
