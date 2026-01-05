from fastapi import FastAPI, Depends, HTTPException
import httpx
from .models import ClientCreate, ClientUpdate, ClientOut, ScoreOut
from . import client as client_module


def get_dynamic_http_client():
    return client_module.get_http_client()


app = FastAPI(title="JAVER Gateway Service", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "storage"}


@app.get("/clients", response_model=list[ClientOut])
def list_clients(client: httpx.Client = Depends(get_dynamic_http_client)):
    r = client.get("/clients")
    r.raise_for_status()
    return r.json()


@app.get("/clients/{client_id}", response_model=ClientOut)
def get_client(client_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    r = client.get(f"/clients/{client_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    return r.json()


@app.post("/clients", response_model=ClientOut, status_code=201)
def create_client(payload: ClientCreate, client: httpx.Client = Depends(get_dynamic_http_client)):
    r = client.post("/clients", json=payload.model_dump())
    r.raise_for_status()
    return r.json()


@app.put("/clients/{client_id}", response_model=ClientOut)
def update_client(client_id: int, payload: ClientUpdate, client: httpx.Client = Depends(get_dynamic_http_client)):
    r = client.put(f"/clients/{client_id}", json=payload.model_dump())
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    return r.json()


@app.delete("/clients/{client_id}", status_code=204)
def delete_client(client_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
    r = client.delete(f"/clients/{client_id}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    r.raise_for_status()
    return


@app.get("/clients/{client_id}/score", response_model=ScoreOut)
def score_credito(client_id: int, client: httpx.Client = Depends(get_dynamic_http_client)):
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
