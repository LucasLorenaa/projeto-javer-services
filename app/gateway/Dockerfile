
FROM python:3.11-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala curl para o healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
# requirements.txt is inside app/gateway when building from repo root context
COPY app/gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o subdiretório do gateway para /srv/gateway
COPY app/gateway ./gateway

# Garante import do pacote "gateway"
ENV PYTHONPATH=/srv
ENV STORAGE_BASE_URL=http://storage:8001

EXPOSE 8000
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
