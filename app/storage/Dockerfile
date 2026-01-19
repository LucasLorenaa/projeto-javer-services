
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala curl para o healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY . ./storage

# Garantir import do pacote "storage"
ENV PYTHONPATH=/srv

# Configurações PostgreSQL
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=javer_db
ENV DB_USER=postgres
ENV DB_PASS=postgres

EXPOSE 8001
CMD ["uvicorn", "storage.main:app", "--host", "0.0.0.0", "--port", "8001"]
