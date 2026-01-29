# 🏦 JAVER Microservices

> Sistema de gerenciamento bancário com arquitetura de microserviços em FastAPI  
> **Cobertura de Testes: 95%** 🎉 | **239 Testes (239 pass / 1 skip)** ✅ | **Python 3.11** 🐍

> **🆕 Novidades:** Sistema completo de investimentos com integração Yahoo Finance, cálculos de patrimônio e projeção de retorno!

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Como Testar](#-como-testar)
- [Testes & Cobertura](#-testes--cobertura)
- [Tipos de Investimento](#-tipos-de-investimento-disponíveis)
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
- API proxy CRUD para clientes e investimentos
- Cálculo de score de crédito
- Sistema de login/registro
- **Gestão completa de investimentos** 📈
- **Integração Yahoo Finance** (cotações em tempo real)
- **Analytics financeiros** (patrimônio, projeção de retorno)
- Frontend responsivo (HTML/CSS/JS)
- Validação com Pydantic
- Cliente HTTP assíncrono

### 💾 **Storage Service** (porta 8001)
- Persistência com SQLite (dev) ou PostgreSQL (prod)
- Repository pattern
- **Sistema de investimentos** com tipos: Ações, Renda Fixa, Fundos, CDB, Tesouro, Crypto
- **Gestão de patrimônio** (conta corrente + investimentos)
- Validação de senha forte
- Verificação HIBP Pwned Passwords
- Hash bcrypt para senhas
- Migrations automáticas

## 📊 Testes & Cobertura

```
✅ 239 testes PASSANDO | 1 skip
❌ 0 testes FALHANDO
📊 95% cobertura geral (app/)
⏱️  ~30-35 segundos local / <45s em CI
```

### 🔧 Últimas Correções (Jan 2026)

- ✅ Corrigido erro de `autocommit` no SQLite
- ✅ Corrigido `KeyError: patrimonio_investimento` no repository
- ✅ Corrigido cálculo de patrimônio total (saldo_cc + investimentos)
- ✅ Corrigido cálculo de projeção de retorno anual
- ✅ Adicionados testes de validação de modelos
- ✅ Compatibilidade total com dicts e objetos em investimentos

### Cobertura por Serviço

**Gateway:**
| Módulo | Cobertura | Linhas Não Cobertas |
|--------|-----------|---------------------|
| `__init__.py` | 100% ✅ | - |
| `main.py` | 100% ✅ | - |
| `models.py` | 98% ✅ | Validators de data (20, 43, 76) |
| `client.py` | 91% ⚠️ | Linha 8 (import path) |
| `yahoo_finance_service.py` | 100% ✅ | - |
| **Total** | **98%** ✅ | |

**Storage:**
| Módulo | Cobertura | Linhas Não Cobertas |
|--------|-----------|---------------------|
| `__init__.py` | 100% ✅ | - |
| `main.py` | 97% ✅ | Logger init (16-17), error handlers |
| `models.py` | 97% ✅ | Validators de data (21, 44, 77) |
| `db.py` | 94% ✅ | PostgreSQL migrations (176-192) |
| `investment_repository.py` | 96% ✅ | PostgreSQL paths (185-190) |
| `repository.py` | 85% ⚠️ | PostgreSQL paths, edge cases |
| **Total** | **92%** ✅ | |

> **Nota:** Linhas não cobertas são principalmente caminhos específicos de PostgreSQL vs SQLite e validators Pydantic que são difíceis de testar em ambiente unitário.

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
GET /investments.html    # Gestão de investimentos
GET /response.html       # Página de resposta
```

**CRUD de Clientes:**
```bash
GET    /clients                 # Listar clientes
POST   /clients                 # Criar cliente
GET    /clients/{id}            # Obter cliente por ID
PUT    /clients/{id}            # Atualizar cliente
DELETE /clients/{id}            # Deletar cliente
```

**Investimentos:**
```bash
GET    /investments                     # Listar todos investimentos
POST   /investments                     # Criar investimento
GET    /investments/{id}                # Obter investimento
PUT    /investments/{id}                # Atualizar investimento
DELETE /investments/{id}                # Vender/deletar investimento
GET    /investments/cliente/{id}        # Listar por cliente
GET    /investments/cliente/{id}/total  # Total investido
```

**Cálculos & Analytics:**
```bash
GET /calculos/patrimonio/{cliente_id}  # Patrimônio total
GET /calculos/projecao/{cliente_id}    # Projeção de retorno
POST /transfer                         # Transferir saldo conta ↔ investimentos
```

**Autenticação & Contas:**
```bash
POST /login                # Login de cliente
POST /register             # Registrar novo cliente
PUT  /password             # Trocar senha
GET  /clients/{id}/score   # Calcular score de crédito
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
    "nome": "João Silva",
    "email": "joao@example.com",
    "telefone": 21987654321,
    "senha": "SecurePass123!",
    "data_nascimento": "1990-05-15",
    "correntista": true
  }'

# Login
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "joao@example.com",
    "senha": "SecurePass123!"
  }'

# Transferir saldo para investimentos
curl -X POST http://localhost:8000/transfer \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "valor": 1000.0,
    "tipo": "CC_PARA_INVESTIMENTO"
  }'

# Criar investimento
curl -X POST http://localhost:8000/investments \
  -H "Content-Type: application/json" \
  -d '{
    "cliente_id": 1,
    "tipo_investimento": "ACOES",
    "ticker": "PETR4",
    "valor_investido": 500.0
  }'

# Calcular patrimônio total
curl http://localhost:8000/calculos/patrimonio/1

# Projeção de retorno anual
curl http://localhost:8000/calculos/projecao/1

# Health check
curl http://localhost:8000/health
curl http://localhost:8001/health
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
│  │  main.py (~295 stmts, 100% cobertura)    │   │
│  │  • Proxy CRUD + investimentos            │   │
│  │  • Login/Registro                        │   │
│  │  • Score de crédito                      │   │
│  │  • Servir frontend + investimentos.html  │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  models.py (124 stmts, 98% cobertura)    │   │
│  │  • Validadores Pydantic                  │   │
│  │  • Idade mínima 18 anos                  │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  client.py (11 stmts, 91% cobertura)     │   │
│  │  • Cliente HTTP para storage             │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  yahoo_finance_service.py (98 stmts,     │   │
│  │  100% cobertura)                         │   │
│  │  • Fallback determinístico               │   │
│  │  • Consultas resilientes (yfinance)      │   │
│  └──────────────────────────────────────────┘   │
└────────────────┬────────────────────────────────┘
                 │ HTTP
                 ▼
┌─────────────────────────────────────────────────┐
│       Storage Service (FastAPI - :8001)         │
│  ┌──────────────────────────────────────────┐   │
│  │  main.py (109 stmts, 98% cobertura)      │   │
│  │  • Endpoints CRUD e investimentos        │   │
│  │  • Lifespan events                       │   │
│  └──────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────┐   │
│  │  repository.py (198 stmts, 90% cobertura)│   │
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
- ✅ Patrimônio de investimento
- ✅ Cálculo automático de score de crédito
- ✅ Dashboard com informações do cliente

### 📈 Gestão de Investimentos (Novo!)
- ✅ CRUD completo de investimentos
- ✅ Tipos: Ações, Renda Fixa, Fundos, CDB, Tesouro Direto, Crypto
- ✅ Integração com Yahoo Finance (cotações em tempo real)
- ✅ Cálculo de patrimônio total (conta + investimentos)
- ✅ Projeção de retorno anual por perfil de investidor
- ✅ Analytics: total investido por cliente
- ✅ Gestão de saldo: transferência conta ↔ investimentos
- ✅ Frontend dedicado: `investments.html`
- ✅ Validação automática de saldo disponível

### 🎨 Interface
- ✅ Frontend responsivo e moderno
- ✅ Páginas: Index, Login, Registro, Dashboard, **Investimentos**
- ✅ Feedback visual de operações
- ✅ Validação no lado do cliente
- ✅ Integração com Yahoo Finance (cotações em tempo real)
- ✅ Interface de gestão completa de investimentos

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
| Market Data | **yfinance** | latest | Cotações em tempo real |
| Web Requests | **requests** | 2.31+ | HIBP API, integrações |

### Testes & Qualidade
| Componente | Tecnologia | Versão | Uso |
|-----------|-----------|--------|-----|
| Framework Testes | **pytest** | 7.4.3 | Unit/integration tests |
| Cobertura | **pytest-cov** | 4.1.0 | Code coverage |
| HTTP Mocking | **pytest-mock** | 3.12.0 | Mock HTTP calls |
| Total Testes | **239+** | - | 95% coverage |

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
│   ├── 🚪 gateway/                    # Gateway Service (98% coverage)
│   │   ├── main.py                    # Rotas e endpoints (302 stmts) ✅ 100%
│   │   ├── models.py                  # Modelos Pydantic (127 stmts) ✅ 98%
│   │   ├── client.py                  # HTTP client (11 stmts) ⚠️ 91%
│   │   ├── yahoo_finance_service.py   # Yahoo Finance API (98 stmts) ✅ 100%
│   │   ├── __init__.py               
│   │   ├── requirements.txt
│   │   ├── Dockerfile
│   │   └── 🎨 frontend/
│   │       ├── index.html             # Página inicial
│   │       ├── login.html             # Login de clientes
│   │       ├── register.html          # Cadastro
│   │       ├── dashboard.html         # Dashboard
│   │       ├── investments.html       # Gestão de investimentos ⭐ NOVO
│   │       ├── response.html          # Respostas
│   │       ├── app.js                 # Lógica frontend
│   │       └── style.css              # Estilos
│   │
│   ├── 💾 storage/                    # Storage Service (92% coverage)
│   │   ├── main.py                    # Endpoints internos (143 stmts) ✅ 97%
│   │   ├── models.py                  # Modelos de dados (103 stmts) ✅ 97%
│   │   ├── repository.py              # Lógica de negócio (239 stmts) ⚠️ 85%
│   │   ├── investment_repository.py   # Gestão investimentos (91 stmts) ✅ 96% ⭐ NOVO
│   │   ├── db.py                      # Database setup (52 stmts) ✅ 94%
│   │   ├── __init__.py
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   │
│   └── 🧪 tests/                      # 239+ testes (95% coverage)
│       ├── conftest.py                # Fixtures compartilhados
│       ├── gateway/                   # Testes do gateway
│       │   ├── test_gateway_main.py
│       │   ├── test_gateway_endpoints.py
│       │   ├── test_gateway_investments_analytics.py ⭐ NOVO
│       │   ├── test_yahoo_finance_service.py ⭐ NOVO
│       │   ├── test_models_validators_extra.py
│       │   ├── test_client_coverage.py
│       │   └── contract/
│       │       └── test_contract_storage.py
│       └── storage/                   # Testes do storage
│           ├── test_storage_main.py
│           ├── test_storage_endpoints.py
│           ├── test_storage_investment_endpoints.py ⭐ NOVO
│           ├── test_investment_repository_extra.py ⭐ NOVO
│           ├── test_repository_comprehensive.py
│           └── test_models_validators.py
│
├── 🐳 docker-compose.yml              # Orquestração de serviços
├── 📋 Dockerfile.tests                # Container de testes
├── ⚙️  pytest.ini                     # Configuração pytest
├── 📖 README.md                       # Este arquivo
└── 🔧 Makefile                        # Scripts de automação

## 💰 Tipos de Investimento Disponíveis

O sistema suporta os seguintes tipos de investimento:

| Tipo | Enum | Ticker? | Descrição |
|------|------|---------|-----------|
| **Ações** | `ACOES` | ✅ Sim | Ações da Bolsa (ex: PETR4, VALE3) |
| **Renda Fixa** | `RENDA_FIXA` | ❌ Não | Títulos de renda fixa |
| **Fundos** | `FUNDOS` | ✅ Opcional | Fundos de investimento |
| **CDB** | `CDB` | ❌ Não | Certificado de Depósito Bancário |
| **Tesouro Direto** | `TESOURO_DIRETO` | ❌ Não | Títulos do governo |
| **Crypto** | `CRYPTO` | ✅ Sim | Criptomoedas (ex: BTC-USD, ETH-USD) |

### 📊 Perfis de Investidor & Projeção

O sistema calcula projeção de retorno anual baseada no perfil:

| Perfil | Taxa Anual | Aplicação |
|--------|------------|-----------|
| **CONSERVADOR** | 8% | Sobre patrimônio total |
| **MODERADO** | 12% | Sobre patrimônio total |
| **ARROJADO** | 18% | Sobre patrimônio total |

> **Patrimônio Total** = `saldo_cc + total_investido`

### 🔄 Fluxo de Investimento

1. **Transferir saldo:** Conta Corrente → Patrimônio de Investimento
2. **Investir:** Deduz do patrimônio disponível
3. **Vender:** Retorna ao patrimônio de investimento
4. **Transferir de volta:** Patrimônio de Investimento → Conta Corrente

```bash
# Exemplo completo
# 1. Cliente tem R$ 5000 em conta corrente
# 2. Transfere R$ 2000 para investimentos
POST /transfer {"cliente_id": 1, "valor": 2000, "tipo": "CC_PARA_INVESTIMENTO"}

# 3. Investe R$ 1500 em ações
POST /investments {"cliente_id": 1, "tipo": "ACOES", "ticker": "PETR4", "valor": 1500}

# 4. Resultado:
# - Saldo CC: R$ 3000
# - Patrimônio disponível: R$ 500
# - Investido: R$ 1500
# - Patrimônio total: R$ 5000
```
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
- 📊 **95% Cobertura** - 1112 de 1166 statements
- ✅ **239+ Testes** - Todos passando (1 skip)
- 🐍 **Type Hints** - 100% do código
- 📝 **Docstrings** - Funções principais documentadas
- 🇧🇷 **Português** - Comentários e nomes em PT-BR
- 🎯 **PEP 8** - Seguindo convenções Python

### Cobertura Detalhada por Arquivo

**Gateway Service (98% total)**
```
gateway/__init__.py             100% ✅ (completo)
gateway/main.py                 100% ✅ (302 stmts - todos cobertos!)
gateway/yahoo_finance_service.py 100% ✅ (98 stmts - cotações em tempo real)
gateway/models.py                98% ✅ (127 stmts - 3 linhas: validators)
gateway/client.py                91% ⚠️  (11 stmts - 1 linha: import path)
```

**Storage Service (92% total)**
```
storage/__init__.py              100% ✅ (completo)
storage/main.py                   97% ✅ (143 stmts - 5 linhas: error handlers)
storage/models.py                 97% ✅ (103 stmts - 3 linhas: validators)
storage/investment_repository.py  96% ✅ (91 stmts - 4 linhas: PostgreSQL paths)
storage/db.py                     94% ✅ (52 stmts - 3 linhas: PostgreSQL migrations)
storage/repository.py             85% ⚠️  (239 stmts - 35 linhas: PostgreSQL + edge cases)
```

### Linhas Não Cobertas (54 total)

**Justificativas:**
- **PostgreSQL paths** (25 linhas) - Caminhos específicos PostgreSQL vs SQLite
- **Pydantic validators** (9 linhas) - Branches de validação de data raramente acionados
- **Error handlers** (12 linhas) - Edge cases e tratamento de exceções raros
- **Logger init** (2 linhas) - Inicialização do sistema de logging
- **Import paths** (6 linhas) - Caminhos condicionais de importação

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