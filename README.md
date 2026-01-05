# JAVER Microservices

Dois serviços FastAPI com cobertura de testes de 99%:
- **gateway** (porta 8000): API proxy CRUD + cálculo de score
- **storage** (porta 8001): Persistência com H2 (JDBC) ou SQLite

## Rodar local

```powershell
# Ativar ambiente
.\.venv\Scripts\Activate.ps1

# Rodar testes
python -m pytest app/tests/ -v
python -m pytest app/tests/ --cov --cov-report=term

# Ou usar Makefile
make test
make test-cov
```

## Docker

```bash
# Subir serviços
docker compose up --build

# Testar
make docker-test
```

Serviços disponíveis:
- Gateway: http://localhost:8000/docs
- Storage: http://localhost:8001/docs

