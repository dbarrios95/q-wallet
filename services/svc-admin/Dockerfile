# CTRL-11: imagen base oficial de Lambda (Node.js 24) fijada por digest, etapas
# separadas y usuario sin privilegios. Se construye desde la carpeta services/:
#   docker build -f services/svc-admin/Dockerfile services
FROM public.ecr.aws/lambda/nodejs:24@sha256:be4c68f4a679e86ff3539675f27aedb3fada5bd2bbf885875c0ca7c32ac6f2bd AS base

# Etapa de compilación: instala dependencias exactas del package-lock y empaqueta
# el servicio en un solo archivo. Nada de esta etapa llega a la imagen final.
FROM base AS compilacion
WORKDIR /compilacion
COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts --no-audit --no-fund
COPY tsconfig.json esbuild.mjs ./
COPY comun/src ./comun/src
COPY svc-admin/src ./svc-admin/src
RUN node esbuild.mjs svc-admin

# Imagen final: solo el archivo empaquetado, de solo lectura, sin npm ni código fuente.
FROM base AS final
COPY --from=compilacion --chmod=0444 /compilacion/dist/svc-admin/index.mjs ${LAMBDA_TASK_ROOT}/
USER 1000:1000
HEALTHCHECK NONE
CMD ["index.handler"]
