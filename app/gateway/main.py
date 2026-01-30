from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os
from pathlib import Path
from .models import (
    ClientCreate, ClientUpdate, ClientOut, ScoreOut, ClientRegister, ClientLogin, ClientPasswordReset,
    InvestimentoCreate, InvestimentoUpdate, InvestimentoOut, ProjecaoRetorno, PatrimonioCliente, AnaliseMercado
)
from . import client as client_module

# Importar YahooFinanceService apenas quando necessário (importação tardia)


def get_dynamic_http_client():
    return client_module.get_http_client()


app = FastAPI(title="JAVER Gateway Service", version="1.0.0")
# Cache simples para cotações de mercado (TTL 60s)
MARKET_CACHE: dict[str, dict] = {}
CACHE_TTL_SECONDS = 60

frontend_dir = Path(__file__).parent / "frontend"
if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")


@app.get("/")
def index():
    frontend_file = Path(__file__).parent / "frontend" / "index.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Frontend não disponível"}


@app.get("/login.html")
def login_page_html():
    frontend_file = Path(__file__).parent / "frontend" / "login.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Login não disponível"}


@app.get("/login")
def login_page():
    frontend_file = Path(__file__).parent / "frontend" / "login.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Login não disponível"}


@app.get("/register.html")
def register_page_html():
    frontend_file = Path(__file__).parent / "frontend" / "register.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Registro não disponível"}


@app.get("/register")
def register_page():
    frontend_file = Path(__file__).parent / "frontend" / "register.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Registro não disponível"}


@app.get("/response")
def response_page():
    frontend_file = Path(__file__).parent / "frontend" / "response.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Página de resposta não disponível"}


@app.get("/dashboard")
def dashboard_page():
    frontend_file = Path(__file__).parent / "frontend" / "dashboard.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Dashboard não disponível"}


# ROTA EXATA PARA PÁGINA DE INVESTIMENTOS - DEVE VIR ANTES DAS ROTAS /investments/*
@app.get("/investments-page")
def investments_page():
    frontend_file = Path(__file__).parent / "frontend" / "investments.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Página de investimentos não disponível"}


@app.get("/investments.html")
def investments_page_html():
    frontend_file = Path(__file__).parent / "frontend" / "investments.html"
    if frontend_file.exists():
        return FileResponse(str(frontend_file), media_type="text/html")
    return {"message": "Página de investimentos não disponível"}


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway"}


@app.get("/clients", response_model=list[ClientOut])
def list_clients(client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    r = client.get("/clients")
    r.raise_for_status()
    return r.json()


@app.get("/clients/{client_id}", response_model=ClientOut)
def get_client(client_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    r = client.get(f"/clients/{client_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    return r.json()


@app.post("/clients", response_model=ClientOut, status_code=201)
def create_client(payload: ClientCreate, client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    r = client.post("/clients", json=payload.model_dump())
    r.raise_for_status()
    return r.json()


@app.post("/register", response_model=ClientOut, status_code=201)
def api_register(payload: ClientRegister, client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    try:
        # Converter data para string ISO para envio ao storage
        data = payload.model_dump()
        if data.get("data_nascimento"):
            data["data_nascimento"] = data["data_nascimento"].isoformat()
        r = client.post("/register", json=data)
        if r.status_code == 400:
            error = r.json()
            raise HTTPException(status_code=400, detail=error.get("detail", "Erro ao criar conta"))
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 400:
            error = e.response.json()
            raise HTTPException(status_code=400, detail=error.get("detail", "Erro ao criar conta"))
        raise


@app.post("/login", response_model=ClientOut)
def api_login(payload: ClientLogin, client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    try:
        r = client.post("/login", json=payload.model_dump())
        if r.status_code == 401:
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 401:
            raise HTTPException(status_code=401, detail="Email ou senha inválidos")
        raise


@app.put("/clients/{client_id}", response_model=ClientOut)
def update_client(client_id: int, payload: ClientUpdate, client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    # Converter data para string ISO se fornecida
    data = payload.model_dump(exclude_unset=True)
    if data.get("data_nascimento"):
        data["data_nascimento"] = data["data_nascimento"].isoformat()
    r = client.put(f"/clients/{client_id}", json=data)
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    return r.json()


@app.delete("/clients/{client_id}", status_code=204)
def delete_client(client_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    r = client.delete(f"/clients/{client_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    return


@app.put("/password", status_code=200)
def update_password(payload: ClientPasswordReset, client: httpx.Client = Depends(get_dynamic_http_client)):
    """Endpoint para resetar senha de forma segura."""
    client = client or client_module.get_http_client()
    try:
        r = client.put("/password", json=payload.model_dump())
        if r.status_code == 404:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        raise


@app.get("/clients/{client_id}/score", response_model=ScoreOut)
def score_credito(client_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    client = client or client_module.get_http_client()
    r = client.get(f"/clients/{client_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    data = r.json()
    saldo = data.get("saldo_cc")
    score_calculado = (saldo * 0.1) if saldo is not None else None
    return {
        "id": data["id"],
        "nome": data["nome"],
        "saldo_cc": saldo,
        "score_calculado": score_calculado,
    }


# ============ ENDPOINTS DE INVESTIMENTOS ============

@app.get("/investments", response_model=list[InvestimentoOut])
def list_investments(client: httpx.Client = Depends(get_dynamic_http_client)):
    """Lista todos os investimentos."""
    from fastapi.responses import JSONResponse
    client = client or client_module.get_http_client()
    r = client.get("/investments")
    r.raise_for_status()
    return JSONResponse(
        content=r.json(),
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/investments/{investment_id}", response_model=InvestimentoOut)
def get_investment(investment_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    """Obtém um investimento específico."""
    client = client or client_module.get_http_client()
    r = client.get(f"/investments/{investment_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    r.raise_for_status()
    return r.json()


@app.get("/investments/cliente/{cliente_id}", response_model=list[InvestimentoOut])
def list_investments_by_cliente(cliente_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    """Lista investimentos de um cliente."""
    from fastapi.responses import JSONResponse
    client = client or client_module.get_http_client()
    r = client.get(f"/investments/cliente/{cliente_id}")
    r.raise_for_status()
    return JSONResponse(
        content=r.json(),
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.post("/investments", response_model=InvestimentoOut, status_code=201)
def create_investment(payload: InvestimentoCreate, client: httpx.Client = Depends(get_dynamic_http_client)):
    """Cria um novo investimento."""
    from .yahoo_finance_service import YahooFinanceService
    
    client = client or client_module.get_http_client()
    
    # Validar ticker se fornecido
    if payload.ticker and not YahooFinanceService.validar_ticker(payload.ticker):
        raise HTTPException(status_code=400, detail=f"Ticker '{payload.ticker}' não encontrado")
    
    r = client.post("/investments", json=payload.model_dump())
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    return r.json()


@app.put("/investments/{investment_id}", response_model=InvestimentoOut)
def update_investment(investment_id: int, payload: InvestimentoUpdate, client: httpx.Client = Depends(get_dynamic_http_client)):
    """Atualiza um investimento."""
    from .yahoo_finance_service import YahooFinanceService
    
    client = client or client_module.get_http_client()
    
    # Validar ticker se fornecido
    if payload.ticker and not YahooFinanceService.validar_ticker(payload.ticker):
        raise HTTPException(status_code=400, detail=f"Ticker '{payload.ticker}' não encontrado")
    
    r = client.put(f"/investments/{investment_id}", json=payload.model_dump(exclude_unset=True))
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    r.raise_for_status()
    return r.json()


@app.delete("/investments/{investment_id}", status_code=204)
def delete_investment(investment_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    """Deleta um investimento."""
    client = client or client_module.get_http_client()
    r = client.delete(f"/investments/{investment_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    r.raise_for_status()
    return


# ============ ENDPOINTS DE CÁLCULOS E ANÁLISES ============

@app.get("/calculos/projecao/{cliente_id}", response_model=ProjecaoRetorno)
def projecao_retorno(cliente_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    """
    Calcula projeção de retorno anual baseada no perfil do investidor.
    
    CONSERVADOR → (total_investido) * 0.08 (8%)
    MODERADO → (total_investido) * 0.12 (12%)
    ARROJADO → (total_investido) * 0.18 (18%)
    
    Onde total_investido é o valor efetivamente aplicado em investimentos ativos
    """
    client = client or client_module.get_http_client()
    
    # Obter dados do cliente
    r = client.get(f"/clients/{cliente_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    cliente_data = r.json()
    
    # Obter total investido
    r_total = client.get(f"/investments/cliente/{cliente_id}/total")
    if r_total.status_code == 404:
        total_investido = 0.0
    else:
        total_investido = r_total.json().get("total_investido", 0.0)
    
    # Usar total investido como base da projeção
    patrimonio_total = total_investido
    perfil = cliente_data.get("perfil_investidor", "CONSERVADOR")
    
    # Calcular taxa de retorno baseada no perfil sobre o patrimônio total
    taxas = {
        "CONSERVADOR": 0.08,
        "MODERADO": 0.12,
        "ARROJADO": 0.18
    }
    
    taxa_retorno = taxas.get(perfil, 0.08)
    projecao_anual = patrimonio_total * taxa_retorno
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={
            "cliente_id": cliente_id,
            "nome": cliente_data.get("nome"),
            "perfil_investidor": perfil,
            "patrimonio_total": patrimonio_total,
            "projecao_anual": round(projecao_anual, 2),
            "taxa_retorno": taxa_retorno * 100
        },
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/calculos/patrimonio/{cliente_id}", response_model=PatrimonioCliente)
def calcular_patrimonio(cliente_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    """Calcula o patrimônio total de um cliente."""
    from fastapi import Response
    client = client or client_module.get_http_client()
    
    # Obter dados do cliente
    r = client.get(f"/clients/{cliente_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    cliente_data = r.json()
    
    # Obter total investido
    r_total = client.get(f"/investments/cliente/{cliente_id}/total")
    if r_total.status_code == 404:
        total_investimentos = 0.0
    else:
        total_investimentos = r_total.json().get("total_investido", 0.0)
    
    saldo_conta = cliente_data.get("saldo_cc") or 0.0
    patrimonio_investimento = cliente_data.get("patrimonio_investimento") or 0.0
    # Patrimônio total = saldo em conta + patrimônio disponível + total investido
    patrimonio_total = saldo_conta + patrimonio_investimento + total_investimentos
    
    from fastapi.responses import JSONResponse
    return JSONResponse(
        content={
            "cliente_id": cliente_id,
            "nome": cliente_data.get("nome"),
            "saldo_conta": saldo_conta,
            "patrimonio_investimento": patrimonio_investimento,
            "total_investimentos": total_investimentos,
            "patrimonio_total": patrimonio_total
        },
        headers={
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )


@app.get("/analises/carteira/{cliente_id}")
def analise_carteira(cliente_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    """
    Analisa a carteira de investimentos de um cliente.
    Retorna informações sobre alocação por tipo de investimento.
    """
    client = client or client_module.get_http_client()
    
    # Obter cliente
    r = client.get(f"/clients/{cliente_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    
    # Obter investimentos
    r_inv = client.get(f"/investments/cliente/{cliente_id}")
    investimentos = r_inv.json() if r_inv.status_code == 200 else []
    
    # Agrupar por tipo
    por_tipo = {}
    total_investido = 0.0
    
    for inv in investimentos:
        tipo = inv.get("tipo_investimento", "DESCONHECIDO")
        valor = inv.get("valor_investido", 0)
        
        if tipo not in por_tipo:
            por_tipo[tipo] = {"quantidade": 0, "total": 0.0, "ativos": 0}
        
        por_tipo[tipo]["quantidade"] += 1
        por_tipo[tipo]["total"] += valor
        total_investido += valor
        
        if inv.get("ativo", False):
            por_tipo[tipo]["ativos"] += 1
    
    # Calcular percentuais
    alocacao = {}
    for tipo, dados in por_tipo.items():
        percentual = (dados["total"] / total_investido * 100) if total_investido > 0 else 0
        alocacao[tipo] = {
            "quantidade": dados["quantidade"],
            "total": round(dados["total"], 2),
            "ativos": dados["ativos"],
            "percentual_carteira": round(percentual, 2)
        }
    
    return {
        "cliente_id": cliente_id,
        "total_investido": round(total_investido, 2),
        "numero_investimentos": len(investimentos),
        "alocacao_por_tipo": alocacao
    }


@app.get("/analises/mercado/{ticker}", response_model=AnaliseMercado)
def analise_mercado(ticker: str, client: httpx.Client = Depends(get_dynamic_http_client)):
    """
    Analisa informações de mercado de um ticker.
    Retorna dados atuais do Yahoo Finance.
    """
    from .yahoo_finance_service import YahooFinanceService
    
    try:
        # Cache: retorna dados recentes se disponíveis
        from time import time
        now = time()
        cached = MARKET_CACHE.get(ticker)
        if cached and (now - cached.get("ts", 0)) < CACHE_TTL_SECONDS:
            info = cached["info"]
        else:
            info = YahooFinanceService.get_ticker_info(ticker)
            if not info:
                # Yahoo indisponível → usar fallback rápido para não deixar tela vazia
                info = YahooFinanceService.get_fallback_info(ticker)
            if info:
                MARKET_CACHE[ticker] = {"info": info, "ts": now}
        
        if not info:
            # Retorno alternativo amigável quando serviço externo falha ou sem internet
            return {
                "ticker": ticker,
                "preco_atual": 0.0,
                "variacao_dia": 0.0,
                "variacao_percentual": 0.0,
                "volume": 0,
                "historico_disponivel": False
            }
        
        return {
            "ticker": ticker,
            "preco_atual": info.get("preco_atual"),
            "variacao_dia": info.get("variacao_dia"),
            "variacao_percentual": info.get("variacao_percentual"),
            "volume": info.get("volume"),
            "historico_disponivel": True
        }
    except Exception:
        # Fallback genérico em caso de exceção
        return {
            "ticker": ticker,
            "preco_atual": 0.0,
            "variacao_dia": 0.0,
            "variacao_percentual": 0.0,
            "volume": 0,
            "historico_disponivel": False
        }
