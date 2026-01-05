
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Instala Java e curl para o healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o h2.jar previamente baixado
COPY h2.jar /opt/h2/h2.jar
ENV H2_JAR_PATH=/opt/h2/h2.jar

# Copia o código
COPY . ./storage

# Garantir import do pacote "storage"
ENV PYTHONPATH=/srv

# Banco em arquivo sob /srv/data
ENV JDBC_URL=jdbc:h2:/srv/data/javer.db;AUTO_SERVER=TRUE
ENV JDBC_USER=sa
ENV JDBC_PASS=

RUN mkdir -p /srv/data
VOLUME ["/srv/data"]

EXPOSE 8001
CMD ["uvicorn", "storage.main:app", "--host", "0.0.0.0", "--port", "8001"]
