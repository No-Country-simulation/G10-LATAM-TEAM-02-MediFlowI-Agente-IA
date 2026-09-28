// Une referencias externas sin modificar el contrato ni eliminar schemas.
import { writeFile } from 'node:fs/promises';
import { bundle, createConfig } from '@redocly/openapi-core';
const [input, output] = process.argv.slice(2);
if (!input || !output) throw new Error('Uso: node bundle_spec.mjs entrada.yaml salida.json');
const result = await bundle({ ref: input, config: await createConfig({}), dereference: false });
const errors = result.problems.filter((problem) => problem.severity === 'error');
if (errors.length) throw new Error(errors.map((problem) => problem.message).join('\n'));
if (result.bundle.parsed.openapi !== '3.1.0') throw new Error('Se requiere OpenAPI 3.1.0');
await writeFile(output, JSON.stringify(result.bundle.parsed, null, 2) + '\n', 'utf8');
