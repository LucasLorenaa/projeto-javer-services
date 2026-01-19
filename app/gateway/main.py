from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import httpx
import os
from pathlib import Path
from .models import ClientCreate, ClientUpdate, ClientOut, ScoreOut, ClientRegister, ClientLogin, ClientPasswordReset
from . import client as client_module


def get_dynamic_http_client():
    return client_module.get_http_client()


app = FastAPI(title="JAVER Gateway Service", version="1.0.0")

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