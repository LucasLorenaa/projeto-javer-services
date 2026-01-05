from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from storage.db import init_db
from storage.models import ClientCreate, ClientUpdate, ClientOut
from storage.repository import list_clients, get_client, create_client, update_client, delete_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    yield
    # Shutdown (if needed)


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
    return create_client(payload.model_dump())

@app.put("/clients/{client_id}", response_model=ClientOut)
def api_update_client(client_id: int, payload: ClientUpdate):
    updated = update_client(client_id, payload.model_dump(exclude_unset=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return updated

@app.delete("/clients/{client_id}", status_code=204)
def api_delete_client(client_id: int):
    ok = delete_client(client_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return
