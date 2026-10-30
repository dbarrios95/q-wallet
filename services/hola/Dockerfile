# CTRL-11: imagen base oficial de Lambda fijada por digest, etapas separadas
# y usuario sin privilegios. Provisional del bloque 1 (ver index.mjs).
FROM public.ecr.aws/lambda/nodejs:24@sha256:be4c68f4a679e86ff3539675f27aedb3fada5bd2bbf885875c0ca7c32ac6f2bd AS base

FROM base AS final
COPY --chmod=0444 index.mjs ${LAMBDA_TASK_ROOT}/
USER 1000:1000
HEALTHCHECK NONE
CMD ["index.handler"]
