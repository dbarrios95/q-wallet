# CTRL-11: imagen base oficial de Lambda (Node.js 24) fijada por digest, etapas
# separadas y usuario sin privilegios. Se construye desde la carpeta services/:
#   docker build -f services/svc-accounts/Dockerfile services
FROM public.ecr.aws/lambda/nodejs:24@sha256:8bc0d3a010f3503f4b028c132c1b589740442a48f389df2648a3d3b485ccfbd3 AS base

# Etapa de compilación: instala dependencias exactas del package-lock y empaqueta
# el servicio en un solo archivo. Nada de esta etapa llega a la imagen final.
FROM base AS compilacion
WORKDIR /compilacion
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY tsconfig.json esbuild.mjs ./
COPY comun/src ./comun/src
COPY svc-accounts/src ./svc-accounts/src
RUN node esbuild.mjs svc-accounts

# Imagen final: solo el archivo empaquetado, de solo lectura, sin código fuente.
# HAL-05: se quitan de la imagen base npm, npx, corepack, el emulador local de Lambda
# (aws-lambda-rie) y la copia del SDK de AWS que trae el runtime: el servicio lleva su propio
# SDK empaquetado, Lambda no usa los demás y traían 24 vulnerabilidades HIGH (Trivy, EVD-3-05).
# La prueba de humo (scripts/humo_lambda.py, EVD-3-15) comprueba que el runtime sigue arrancando.
FROM base AS final
RUN rm -rf /var/lang/lib/node_modules/npm /var/lang/lib/node_modules/corepack \
      /var/lang/bin/npm /var/lang/bin/npx /var/lang/bin/corepack /usr/local/bin/aws-lambda-rie \
      /var/runtime/node_modules/@aws-sdk
COPY --from=compilacion --chmod=0444 /compilacion/dist/svc-accounts/index.mjs ${LAMBDA_TASK_ROOT}/
USER 1000:1000
HEALTHCHECK NONE
CMD ["index.handler"]
