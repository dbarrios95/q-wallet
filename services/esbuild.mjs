// Empaqueta cada microservicio en un solo archivo index.mjs (sin node_modules en la imagen).
// Uso: node esbuild.mjs [svc-...]   (sin argumento: los cinco)
import { build } from "esbuild";

const SERVICIOS = ["svc-profile", "svc-accounts", "svc-transfers", "svc-budgets", "svc-admin"];
const pedidos = process.argv.slice(2);
const lista = pedidos.length ? pedidos : SERVICIOS;

for (const s of lista) {
  if (!SERVICIOS.includes(s)) {
    console.error(`Servicio desconocido: ${s}`);
    process.exit(1);
  }
  await build({
    entryPoints: [`${s}/src/handler.ts`],
    outfile: `dist/${s}/index.mjs`,
    bundle: true,
    platform: "node",
    target: "node24",
    format: "esm",
    minify: false,
    sourcemap: false,
    legalComments: "none",
    // El SDK de AWS v3 usa require() en algunos módulos internos.
    banner: { js: "import { createRequire } from 'node:module'; const require = createRequire(import.meta.url);" },
    logLevel: "warning",
  });
  console.log(`${s}: dist/${s}/index.mjs`);
}
