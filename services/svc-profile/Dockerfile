# CTRL-11: imagen base oficial de Lambda (Node.js 24) fijada por digest, etapas
# separadas y usuario sin privilegios. Se construye desde la carpeta services/:
#   docker build -f services/svc-profile/Dockerfile services
FROM public.ecr.aws/lambda/nodejs:24@sha256:8bc0d3a010f3503f4b028c132c1b589740442a48f389df2648a3d3b485ccfbd3 AS base

# Etapa de compilación: instala dependencias exactas del package-lock y empaqueta
# el servicio en un solo archivo. Nada de esta etapa llega a la imagen final.
FROM base AS compilacion
WORKDIR /compilacion
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY tsconfig.json esbuild.mjs ./
COPY comun/src ./comun/src
COPY svc-profile/src ./svc-profile/src
RUN node esbuild.mjs svc-profile

# Imagen final: solo el archivo empaquetado, de solo lectura, sin código fuente.
# HAL-05: se quitan npm, npx, corepack y el emulador local de Lambda (aws-lambda-rie):
# vienen en la imagen base, Lambda no los usa y traían vulnerabilidades HIGH (Trivy, EVD-3-05).
FROM base AS final
RUN rm -rf /var/lang/lib/node_modules/npm /var/lang/lib/node_modules/corepack \
      /var/lang/bin/npm /var/lang/bin/npx /var/lang/bin/corepack /usr/local/bin/aws-lambda-rie
COPY --from=compilacion --chmod=0444 /compilacion/dist/svc-profile/index.mjs ${LAMBDA_TASK_ROOT}/
USER 1000:1000
HEALTHCHECK NONE
CMD ["index.handler"]
