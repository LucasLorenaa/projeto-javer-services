# 🏦 JAVER Microservices

> Sistema de gerenciamento bancário com arquitetura de microserviços em FastAPI  
> **Cobertura de Testes: 93%** 🎉 | **154 Testes** ✅ | **Python 3.11** 🐍

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Como Testar](#-como-testar)
- [Testes & Cobertura](#-testes--cobertura)
- [Arquitetura](#-arquitetura)
- [Funcionalidades](#-funcionalidades)
- [Quick Start](#-quick-start)
- [APIs](#-apis)
- [Stack Tecnológico](#-stack-tecnológico)
- [Segurança](#-segurança)
- [Contribuindo](#-contribuindo)

---

## 🎯 Visão Geral

Sistema bancário completo com dois serviços FastAPI independentes e bem estruturados:

### 🚪 **Gateway Service** (porta 8000)
- API proxy CRUD para clientes
- Cálculo de score de crédito
- Sistema de login/registro
- Frontend responsivo (HTML/CSS/JS)
- Validação com Pydantic
- Cliente HTTP assíncrono

### 💾 **Storage Service** (porta 8001)
- Persistência com SQLite (dev) ou PostgreSQL (prod)
- Repository pattern
- Validação de senha forte
- Verificação HIBP Pwned Passwords
- Hash bcrypt para senhas
- Migrations automáticas

## 📊 Testes & Cobertura

```
✅ 154 testes PASSANDO
❌ 0 testes FALHANDO
📊 93% cobertura geral (574/615 statements)
⏱️  ~3 segundos para rodar
```

### Cobertura por Serviço

**Gateway:**
| Módulo | Cobertura |
|--------|-----------|
| `__init__.py` | 100% ✅ |
| `main.py` | 99% ✅ |
| `models.py` | 95% ✅ |
| `client.py` | 100% ✅ |
| **Total** | **99%** ✅ |

**Storage:**
| Módulo | Cobertura |
|--------|-----------|
| `__init__.py` | 100% ✅ |
| `main.py` | 94% ✅ |
| `models.py` | 93% ✅ |
| `db.py` | 95% ✅ |
| `repository.py` | 88% ✅ |
| **Total** | **92%** ✅ |

## 🧪 Como Testar

### Opção 1: Docker Compose (Recomendado)

```bash
# 1. Subir os serviços
docker-compose up --build -d

# 2. Acessar os serviços
- Gateway:  http://localhost:8000
- Storage:  http://localhost:8001
- Postgres: localhost:5432

# 3. Testar health check
curl http://localhost:8000/health
curl http://localhost:8001/health

# 4. Parar os serviços
docker-compose down
```

### Opção 2: Executar Testes Automatizados

```bash
# Via Docker (mais rápido)
docker run --rm javer-tests pytest --cov=gateway --cov=storage --cov-report=term-missing -q

# Localmente com pytest
pytest app/tests/ -v --cov=app --cov-report=html
```

### Opção 3: Testar Manualmente via Swagger UI

1. **Gateway Swagger:** http://localhost:8000/docs
2. **Storage Swagger:** http://localhost:8001/docs

Você pode fazer requisições diretamente na interface!

## 🚀 Quick Start

### Pré-requisitos
- Python 3.10+
- Docker & Docker Compose (opcional)

### Instalação  (recomendado!)
docker-compose up --build -d

# Ver logs
docker-compose logs -f gateway
docker-compose logs -f storage

# Parar
docker-compose down

# Parar e remover volumes
docker-compose down -v
```

## 🌐 APIs

### ✨ Endpoints Disponíveis

#### Gateway (http://localhost:8000)

**Documentação interativa:** http://localhost:8000/docs (Swagger)

**Página Inicial:**
```bash
GET /                    # Página inicial (index.html)
GET /login.html          # Login
GET /register.html       # Registro
GET /dashboard.html      # Dashboard
GET /response.html       # Página de resposta
```

**CRUD de Clientes:**
```bash
GET    /clients                 # Listar clientes
POST   /clients                 # Criar cliente
GET    /clients/{email}         # Obter cliente
PUT    /clients/{email}         # Atualizar cliente
DELETE /clients/{email}         # Deletar cliente
```

**Autenticação & Contas:**
```bash
POST /login                # Login de cliente
POST /register             # Registrar novo cliente
POST /password             # Trocar senha
POST /score                # Calcular score de crédito
GET  /health               # Health check
```

#### Storage (http://localhost:8001)

**Documentação interativa:** http://localhost:8001/docs (Swagger)

**Endpoints (mesmo padrão do gateway):**
```bash
GET    /clients                 # Listar clientes
POST   /clients                 # Criar cliente
GET    /clients/{email}         # Obter cliente
PUT    /clients/{email}         # Atualizar cliente
DELETE /clients/{email}         # Deletar cliente
POST   /login                   # Login
POST   /register                # Registrar
POST   /password                # Trocar senha
GET    /health                  # Health check
```

### Exemplos de Requisições

```bash
# Registrar novo cliente
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "SecurePass123",
    "nome": "João Silva",
    "data_nascimento": "1990-05-15"
  }'

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "SecurePass123"
  }'

# Calcular score
curl -X POST http://localhost:8000/score \
  -H "Content-Type: application/json" \
  -d '{"email": "joao@example.com"}'

# Health check
curl http://localhost:8000/health
curl http://localhost:8001/health
**Endpoints CRUD:**
```bash
# Criar cliente
POST /clients

# Listar clientes
GET /clients

# Obter cliente
GET /clients/{email}

# Atualizar cliente
PUT /clients/{email}

# Deletar cliente
DELETE /clients/{email}
```

**Endpoints Adicionais:**
```bash
# Login
POST /login

# Trocar senha
POST /password

# Calcular score de crédito
POST /score
```

### Storage (http://localhost:8001)

**Documentação interativa:** http://localhost:8001/docs (Swagger)

**Endpoints Internos:**
```bash
# Mesmo padrão CRUD do gateway
GET/POST/PUT/DELETE /clients
```

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│           Frontend (HTML/CSS/JS)                │
│  Login | Registro | Dashboard | Response        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│       Gateway Service (FastAPI - :8000)         │
│  ┌──────────────────────────────────────────┐   │
│  │  main.py (153 lines, 99% coverage)       │   │
│  │  • Proxy CRUD                            │   │
│  │  • Login/Registro                        │   │
│  │  • Score de crédito                      │   │
│  │  • Servir frontend                       │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  models.py (74 lines, 95% coverage)      │   │
│  │  • Validadores Pydantic                  │   │
│  │  • Idade mínima 18 anos                  │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  client.py (11 lines, 100% coverage)     │   │
│  │  • Cliente HTTP para storage             │   │
│  └──────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────┘
                 │ HTTP
                 ▼
┌─────────────────────────────────────────────────┐
│       Storage Service (FastAPI - :8001)         │
│  ┌──────────────────────────────────────────┐   │
│  │  main.py (65 lines, 94% coverage)        │   │
│  │  • Endpoints CRUD                        │   │
│  │  • Lifespan events                       │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  repository.py (204 lines, 88% coverage) │   │
│  │  • Lógica de negócio                     │   │
│  │  • Hash bcrypt                           │   │
│  │  • HIBP API integration                  │   │
│  │  • Cálculo de score                      │   │
│  └──────────────────────────────────────────┘   │
│  ✨ Funcionalidades

### 🔐 Autenticação & Segurança
- ✅ Registro de clientes com validação completa
- ✅ Login com email/senha
- ✅ Hash bcrypt para senhas
- ✅ Verificação HIBP Pwned Passwords (k-anonimidade)
- ✅ Validação de senha forte (min. 6 chars, sem senhas comuns)
- ✅ Validação de idade mínima (18 anos)

### 👥 Gestão de Clientes
- ✅ CRUD completo (Create, Read, Update, Delete)
- ✅ Listagem de todos os clientes
- ✅ Busca por email
- ✅ Atualização de dados pessoais
- ✅ Atualização de senha com validação

### 💳 Funcionalidades Bancárias
- ✅ Indicador de correntista
- ✅ Saldo em conta corrente
- ✅ Cálculo automático de score de crédito
- ✅ Dashboard com informações do cliente

### 🎨 Interface
- ✅ Frontend responsivo
- ✅ Páginas: Index, Login, Registro, Dashboard
- ✅ Feedback visual de operações
- ✅ Validação no lado do cliente

## 🛠️ Stack Tecnológico

### Backend
| Componente | Tecnologia | Versão | Uso |
|-----------|-----------|--------|-----|
| Framework Web | **FastAPI** | 0.109.0 | API REST async |
| Validação | **Pydantic** | v1 | Modelos e validação |
| HTTP Client | **httpx** | 0.25.2 | Comunicação inter-serviços |
| Hash Senha | **bcrypt** | 4.1.0 | Criptografia de senhas |
| Banco Dados | **PostgreSQL** | 15+ | Produção |
| Banco Dados | **SQLite** | 3.x | Desenvolvimento/testes |
| DB Driver | **psycopg2** | 2.9.9 | PostgreSQL adapter |

### Testes & Qualidade
| Componente | Tecnologia | Versão | Uso |
|-----------|-----------|--------|-----|
| Framework Testes | **pytest** | 7.4.3 | Unit/integration tests |
| Cobertura | **pytest-cov** | 4.1.0 | Code coverage |
| HTTP Mocking | **pytest-mock** | 3.12.0 | Mock HTTP calls |
| Total Testes | **230+** | - | 93% coverage |

### DevOps & Infraestrutura
| Componente | Tecnologia | Versão | Uso |
|-----------|-----------|--------|-----|
| Container | **Docker** | 24.x | Containerização |
| Orquestração | **Docker Compose** | 2.x | Multi-container |
| Python | **Python** | 3.11 | Runtime |

### Frontend
| Componente | Tecnologia | Descrição |
|-----------|-----------|-----------|
| HTML5 | **Vanilla** | Estrutura semântica |
| CSS3 | **Custom** | Estilos responsivos |
| JavaScript | **ES6+** | Interatividade

## 📁 Estrutura do Projeto

```
javer-services/
├── 📦 app/
│   ├── 🚪 gateway/                    # Gateway Service (99% coverage)
│   │   ├── main.py                    # Rotas e endpoints (153 stmts)
│   │   ├── models.py                  # Modelos Pydantic (74 stmts)
│   │   ├── client.py                  # HTTP client (11 stmts)
│   │   ├── __init__.py               
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── 🎨 frontend/
│   │       ├── index.html             # Página inicial
│   │       ├── login.html             # Login de clientes
│   │       ├── register.html          # Cadastro
│   │       ├── dashboard.html         # Dashboard
│   │       ├── response.html          # Respostas
│   │       ├── app.js                 # Lógica frontend
│   │       └── style.css              # Estilos
│   │
│   ├── 💾 storage/                    # Storage Service (92% coverage)
│   │   ├── main.py                    # Endpoints internos (65 stmts)
│   │   ├── models.py                  # Modelos de dados (69 stmts)
│   │   ├── repository.py              # Lógica de negócio (204 stmts)
│   │   ├── db.py                      # Database setup (39 stmts)
│   │   ├── __init__.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── 🧪 tests/                      # 230+ testes (93% coverage)
│  🔒 Segurança

### ✅ Implementado
- ✅ **Hash bcrypt** para senhas (salt rounds)
- ✅ **HIBP Pwned Passwords** (k-anonimidade) - verifica senhas comprometidas
- ✅ **Validação forte de senha** (mínimo 6 chars, sem senhas comuns)
- ✅ **Validação de dados** com Pydantic
- ✅ **SQL Injection** - parametrização de queries
- ✅ **Type Safety** - Type hints em todo código

### ⚠️ Melhorias Futuras para Produção

#### Crítico
- ❌ **JWT Authentication** - tokens stateless
- ❌ **CORS** - configurar origins permitidos
- ❌ **Rate Limiting** - proteção contra força bruta
- ❌ **HTTPS** - certificado SSL
- ❌ **Secrets Management** - vault para credenciais

#### Recomendado
- ⚠️ **Authorization (RBAC)** - controle de acesso
- ⚠️ **Audit Logging** - log de todas operações
- ⚠️ **Input Sanitization** - sanitizar HTML/JS
- ⚠️ **Session Management** - expiração de sessões
- ⚠️ **2FA** - autenticação dois fatores

#### Exemplo JWT (para produção)
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # Verificar JWT aqui
    if not valid_token(token):
        raise HTTPException(status_code=401, detail="Token inválido")
    return token
```

## 📊 Qualidade do Código

### Métricas
- 📊 **93% Cobertura** - 574 de 615 statements
- ✅ **230+ Testes** - Todos passando
- 🐍 **Type Hints** - 100% do código
- 📝 **Docstrings** - Funções principais documentadas
- 🇧🇷 **Português** - Comentários e nomes em PT-BR
- 🎯 **PEP 8** - Seguindo convenções Python

### Cobertura Detalhada por Arquivo

**Gateway Service (99% total)**
```
gateway/__init__.py    100% ✅ (completo)
gateway/client.py      100% ✅ (completo)  
gateway/main.py         99% ✅ (1 linha: fallback frontend)
gateway/models.py       95% ✅ (4 linhas: validators edge cases)
```

**Storage Service (92% total)**
```
storage/__init__.py    100% ✅ (completo)
storage/db.py           95% ✅ (2 linhas: PostgreSQL error handling)
storage/main.py         94% ✅ (4 linhas: lifespan context)
storage/models.py       93% ✅ (5 linhas: validators edge cases)
storage/repository.py   88% ✅ (25 linhas: PostgreSQL RETURNING paths)
```

### Linhas Não Cobertas (41 total)

**Justificativas:**
- **PostgreSQL paths** (20 linhas) - Difícil testar sem infra PostgreSQL
- **Pydantic validators** (9 linhas) - Parsing flexível impede alguns caminhos
- **Error handlers** (8 linhas) - Edge cases raros
- **Frontend fallback** (1 linha) - Path condicional
- **Lifespan** (3 linhas) - Context manager interno

## ⚙️ Configuração

### Variáveis de Ambiente

**Storage Service (.env):**
```bash
# PostgreSQL (produção)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=javer_db
DB_USER=postgres
DB_PASS=postgres

# Ou usar SQLite (desenvolvimento)
# Nenhuma variável necessária - usa :memory:
```

**Gateway Service:**
```bash
STORAGE_URL=http://storage:8001
# ou http://localhost:8001 para local
```

### Docker Compose
 & Links

### Documentação Online
- 📖 **Swagger UI** - http://localhost:8000/docs (Gateway - interativo)
- 📖 **ReDoc** - http://localhost:8000/redoc (Gateway - visual)
- 📖 **Storage Docs** - http://localhost:8001/docs (Storage service)

### Arquivos do Projeto
- � **[REVISAO_PROJETO.md](REVISAO_PROJETO.md)** - Revisão completa e métricas
- 🛠️ **[MANUTENCAO.md](MANUTENCAO.md)** - Guia de manutenção e limpeza
- 📄 **README.md** - Este arquivo (visão geral)

### Scripts Úteis
- 🧹 **[limpar_projeto.ps1](limpar_projeto.ps1)** - Script de limpeza automática

### Recursos Externos
- 🔐 **HIBP API** - https://haveibeenpwned.com/API/v3
- 🐍 **FastAPI** - https://fastapi.tiangolo.com
- 🧪 **Pytest** - https://docs.pytest.org

## 🧹 Manutenção & Limpeza

### Limpar Arquivos Temporários

O projeto pode acumular arquivos temporários durante desenvolvimento e testes. Use o script de limpeza automática:

```powershell
# Executar script de limpeza
.\limpar_projeto.ps1
```

**O que é removido:**
- `__pycache__/` - Cache Python compilado
- `.pytest_cache/` - Cache do pytest
- `.coverage` - Dados de cobertura
- `htmlcov/` e `cov_report/` - Relatórios HTML
- `*.pyc`, `*.pyo`, `*.pyd` - Bytecode Python
- `*.log` - Arquivos de log

**Resultado esperado:** ~65 itens removidos (incluindo dependências)

**⚠️ Importante:** O script **NÃO remove** código-fonte ou testes, apenas arquivos temporários.

Para mais detalhes sobre manutenção, consulte [MANUTENCAO.md](MANUTENCAO.md)

## 🧪 Testes

### Executar Testes

```bash
# Via Docker (recomendado)
docker run --rm javer-tests pytest --cov=gateway --cov=storage --cov-report=term-missing:skip-covered -q

# Localmente
pytest app/tests/ -v --cov=app --cov-report=html

# Testes específicos
pytest app/tests/gateway/unit/test_main_coverage.py -v
pytest app/tests/storage/test_90_percent_coverage.py -v

# Com detalhes de cobertura
pytest --cov=gateway --cov=storage --cov-report=html
# Abrir: htmlcov/index.html
```

### Estrutura de Testes

```
app/tests/
├── __init__.py
├── conftest.py                    # Fixtures compartilhadas
│
├── gateway/                       # Testes do Gateway (70+ testes)
│   ├── __init__.py
│   ├── test_gateway_main.py          # 30 testes de rotas principais
│   ├── test_gateway_endpoints.py     # 6 testes de validação
│   ├── test_gateway_coverage_gaps.py # 17 testes de casos extremos
│   ├── contract/
│   │   └── test_contract_storage.py  # 1 teste de contrato
│   └── unit/
│       ├── test_main_coverage.py     # 3 testes de cobertura
│       ├── test_models_comprehensive.py  # 15 testes de modelos
│       ├── test_routes_comprehensive.py  # 5 testes de rotas
│       ├── test_client_module.py     # Testes do cliente HTTP
│       ├── test_client_real.py       # Testes reais
│       ├── test_routes_crud.py       # Testes CRUD
│       ├── test_routes_full.py       # Fluxos completos
│       └── test_score_route.py       # Score de crédito
│
└── storage/                       # Testes do Storage (80+ testes)
    ├── __init__.py
    ├── test_storage_main.py          # 24 testes de endpoints
    ├── test_storage_endpoints.py     # 10 testes CRUD
    ├── test_main_endpoints.py        # 13 testes FastAPI
    ├── test_models_comprehensive.py  # 12 testes de modelos
    ├── test_repository_comprehensive.py  # 13 testes de repository
    └── test_remaining_coverage.py    # 3 testes PostgreSQL
```

**Total: 154 testes organizados**

### Tipos de Testes

- ✅ **Unit Tests** - Funções isoladas com mocks
- ✅ **Integration Tests** - Endpoints FastAPI com TestClient
- ✅ **Contract Tests** - Validação de contratos entre serviços
- ✅ **Edge Cases** - Casos extremos e erros
- ⚠️ **E2E Tests** - Ainda não implementado

## 🤝 Contribuindo

### Como Contribuir

1. **Fork** o repositório
2. **Clone** seu fork
   ```bash
   git clone https://github.com/SEU_USUARIO/projeto-javer-services.git
   cd projeto-javer-services
   ```
3. **Criar branch** feature
   ```bash
   git checkout -b feature/minha-feature
   ```
4. **Fazer mudanças** e adicionar testes

5. **Rodar testes** localmente
   ```bash
   pytest app/tests/ -v
   ```
6. **Commit** com mensagem descritiva
   ```bash
   git commit -m 'feat: adiciona autenticação JWT'
   ```
7. **Push** para seu fork
   ```bash
   git push origin feature/minha-feature
   ```
8. **Abrir Pull Request** no GitHub

### Padrões de Commit

Seguimos [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` nova funcionalidade
- `fix:` correção de bug
- `docs:` mudanças em documentação
- `test:` adicionar/modificar testes
- `refactor:` refatoração de código
- `perf:` melhorias de performance
- `chore:` tarefas de build/config

### Checklist para PR

- [ ] Testes adicionados/atualizados
- [ ] Cobertura mantida acima de 90%
- [ ] Docstrings em português
- [ ] Type hints adicionados
- [ ] README atualizado (se necessário)
- [ ] Testes locais passando

## 🐛 Reportar Bugs

Encontrou um bug? Abra uma [issue](https://github.com/LucasLorenaa/projeto-javer-services/issues) com:

1. **Descrição clara** do problema
2. **Passos para reproduzir**
3. **Comportamento esperado** vs **atual**
4. **Screenshots** (se aplicável)
5. **Ambiente** (OS, Python version, Docker version)

## 📜 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

**Lucas Silveira**
- GitHub: [@LucasLorenaa](https://github.com/LucasLorenaa)
- Projeto: [projeto-javer-services](https://github.com/LucasLorenaa/projeto-javer-services)

## 🙏 Agradecimentos

- FastAPI pela framework excelente
- Have I Been Pwned (HIBP) pela API de senhas comprometidas
- Comunidade Python pela stack de testes

## 📈 Estado do Projeto & Roadmap

### ✅ Concluído (v1.0)
- ✅ Arquitetura de microserviços
- ✅ **154 testes organizados por serviço** (Gateway: 70+, Storage: 80+)
- ✅ **93% cobertura de código** (574/615 statements)
- ✅ **Testes otimizados** (removidos 76 testes duplicados, mantendo 100% da cobertura)
- ✅ Docker & Docker Compose (all services healthy)
- ✅ Frontend funcional e responsivo
- ✅ Validação completa com Pydantic
- ✅ Hash de senha com bcrypt
- ✅ HIBP Pwned Passwords integration
- ✅ Cálculo de score de crédito
- ✅ Login/Registro de clientes
- ✅ CRUD completo
- ✅ **Código 100% em português**
- ✅ **Testes organizados em diretórios apropriados**
- ✅ **Projeto limpo e mantível** (repositório otimizado)

### 🚧 Próximas Versões

**v1.1 - Segurança** (prioridade alta)
- [ ] Autenticação JWT
- [ ] CORS configurado
- [ ] Rate limiting (SlowAPI)
- [ ] HTTPS em produção
- [ ] Secrets em vault

**v1.2 - Performance**
- [ ] Connection pooling (asyncpg)
- [ ] Cache Redis
- [ ] Query optimization
- [ ] Lazy loading

**v1.3 - Observabilidade**
- [ ] Logging estruturado (structlog)
- [ ] Metrics (Prometheus)
- [ ] Tracing (OpenTelemetry)
- [ ] Health checks avançados

**v2.0 - Features**
- [ ] Testes E2E (Playwright)
- [ ] Authorization RBAC
- [ ] API Gateway (Kong/Traefik)
- [ ] Event-driven (Kafka/RabbitMQ)
- [ ] Async workers (Celery
### ✅ Implementado
- Arquitetura de microserviços
- 137 testes passando
- 79% cobertura
- Docker & Docker Compose
- Frontend funcional
- Validação com Pydantic
- Hash de senha com bcrypt

### ❌ Faltando para Produção
- **CRÍTICO:** Autenticação (JWT)
- **CRÍTICO:** CORS configurado
- **CRÍTICO:** Rate limiting
- Autorização (RBAC)
- Testes E2E
- Logging estruturado
- Connection pooling
- Cache (Redis)

### 📋 Recomendações

Antes de usar em produção, implementar:

1. **Autenticação JWT**
   ```python
   from fastapi_jwt_extended import JWTManager
   # ... adicionar proteção aos endpoints
   ```

2. **CORS**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   # ... configurar allowed origins
   ```

3. **Rate Limiting**
   ```python
   from slowapi import Limiter
   # ... proteger endpoints de força bruta
   ```

4. **HTTPS em Produção**
   - Configurar certificado SSL
   - Forçar redirecionamento HTTP → HTTPS

5. **Variáveis de Ambiente**
   - Não deixar secrets em código
   - Usar .env com python-dotenv

Veja guia completo em [DOCUMENTACAO.md](DOCUMENTACAO.md)

## 📚 Documentação

- **[DOCUMENTACAO.md](DOCUMENTACAO.md)** - Guia completo (arquitetura, segurança, roadmap, etc.)
- **Swagger UI** - http://localhost:8000/docs (Gateway)
- **ReDoc** - http://localhost:8000/redoc (Gateway)

## 🤝 Contribuindo

1. Fork o repositório
2. Criar branch feature (`git checkout -b feature/minha-feature`)
3. Commit mudanças (`git commit -m 'Add minha-feature'`)
4. Push para branch (`git push origin feature/minha-feature`)
5. Abrir Pull Request


## 👤 Autor

**Lucas Silveira**
- GitHub: [@LucasLorenaa](https://github.com/LucasLorenaa)
- Projeto: [projeto-javer-services](https://github.com/LucasLorenaa/projeto-javer-services)

---