from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import re
from storage.db import init_db
from storage.models import ClientCreate, ClientUpdate, ClientOut, ClientRegister, ClientLogin, ClientPasswordReset, InvestimentoCreate, InvestimentoUpdate, InvestimentoOut
from storage.repository import list_clients, get_client, create_client, update_client, delete_client, login_client, update_password
from storage.investment_repository import InvestmentRepository


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização
    init_db()
    yield
    # Finalização (se necessário)


app = FastAPI(title="JAVER Storage Service", version="1.0.0", lifespan=lifespan)

@app.get("/health")
def health():
    return {"status": "ok", "service": "storage"}

@app.get("/clients", response_model=list[ClientOut])
def api_list_clients():
    return list_clients()

@app.get("/clients/{client_id}", response_model=ClientOut)
def api_get_client(client_id: int):
    c = get_client(client_id)
    if not c:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return c

@app.post("/clients", response_model=ClientOut, status_code=201)
def api_create_client(payload: ClientCreate):
    try:
        return create_client(payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/register", response_model=ClientOut, status_code=201)
def api_register(payload: ClientRegister):
    try:
        return create_client(payload.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/login", response_model=ClientOut)
def api_login(payload: ClientLogin):
    client = login_client(payload.email, payload.senha)
    if not client:
        raise HTTPException(status_code=401, detail="Email ou senha inválidos")
    return client

@app.put("/clients/{client_id}", response_model=ClientOut)
def api_update_client(client_id: int, payload: ClientUpdate):
    try:
        updated = update_client(client_id, payload.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not updated:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return updated

@app.delete("/clients/{client_id}", status_code=204)
def api_delete_client(client_id: int):
    ok = delete_client(client_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return

@app.put("/password", status_code=200)
def api_update_password(payload: ClientPasswordReset):
    """Atualiza a senha de um cliente de forma segura (gera hash bcrypt correto)."""
    # Validação defensiva no endpoint (além do repository)
    pwd = payload.senha_nova
    if len(pwd) < 6:
        raise HTTPException(status_code=400, detail="Senha deve ter ao menos 6 caracteres")
    success = update_password(payload.email, payload.senha_nova)
    if not success:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return {"message": "Senha atualizada com sucesso"}


# ============ ENDPOINTS DE INVESTIMENTOS ============

@app.get("/investments", response_model=list[InvestimentoOut])
def api_list_investments():
    """Lista todos os investimentos."""
    return InvestmentRepository.get_all()


@app.get("/investments/{investment_id}", response_model=InvestimentoOut)
def api_get_investment(investment_id: int):
    """Retorna um investimento específico por ID."""
    inv = InvestmentRepository.get_by_id(investment_id)
    if not inv:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    return inv


@app.get("/investments/cliente/{cliente_id}", response_model=list[InvestimentoOut])
def api_list_investments_by_cliente(cliente_id: int):
    """Lista todos os investimentos de um cliente."""
    return InvestmentRepository.get_by_cliente(cliente_id)


@app.post("/investments", response_model=InvestimentoOut, status_code=201)
def api_create_investment(payload: InvestimentoCreate):
    """Cria um novo investimento."""
    try:
        # Verificar se o cliente existe
        cliente = get_client(payload.cliente_id)
        if not cliente:
            raise HTTPException(status_code=404, detail="Cliente não encontrado")
        
        return InvestmentRepository.create(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.put("/investments/{investment_id}", response_model=InvestimentoOut)
def api_update_investment(investment_id: int, payload: InvestimentoUpdate):
    """Atualiza um investimento."""
    try:
        updated = InvestmentRepository.update(investment_id, payload)
        if not updated:
            raise HTTPException(status_code=404, detail="Investimento não encontrado")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/investments/{investment_id}", status_code=204)
def api_delete_investment(investment_id: int):
    """Deleta um investimento."""
    ok = InvestmentRepository.delete(investment_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Investimento não encontrado")
    return


@app.get("/investments/cliente/{cliente_id}/total")
def api_get_total_investido(cliente_id: int):
    """Retorna o total investido por um cliente."""
    # Verificar se o cliente existe
    cliente = get_client(cliente_id)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    total = InvestmentRepository.get_total_investido_cliente(cliente_id)
    return {"cliente_id": cliente_id, "total_investido": total}
