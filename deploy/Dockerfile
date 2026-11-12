# Imagen del servicio para Cloud Run (T004). Se construye desde la raíz del repositorio:
#   docker build -f deploy/Dockerfile -t proyecta .
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
RUN pip install --no-cache-dir . && rm -rf build src/*.egg-info
USER nobody
ENV PROYECTA_ENV=prod
# Cloud Run (y Render) entregan el puerto en $PORT. Detrás de su proxy, la IP real viene en X-Forwarded-For:
# sin --proxy-headers, el bloqueo por IP (RNF-05) bloquearía a todos a la vez.
CMD exec uvicorn proyecta.main:app --host 0.0.0.0 --port ${PORT:-8080} --proxy-headers --forwarded-allow-ips "*"
