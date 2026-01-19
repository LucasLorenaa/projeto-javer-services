from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
import re
from storage.db import init_db
from storage.models import ClientCreate, ClientUpdate, ClientOut, ClientRegister, ClientLogin, ClientPasswordReset
from storage.repository import list_clients, get_client, create_client, update_client, delete_client, login_client, update_password


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
