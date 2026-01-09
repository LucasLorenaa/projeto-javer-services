from fastapi.testclient import TestClient
from fastapi.testclient import TestClient
from gateway.main import app
import os
from pathlib import Path
import shutil

client = TestClient(app)

def test_gateway_crud_flow():
    r = client.post("/clients", json={"nome":"A","telefone":1,"correntista":True,"saldo_cc":100.0})
    assert r.status_code == 201
    cid = r.json()["id"]

    r = client.get(f"/clients/{cid}")
    assert r.status_code == 200

    r = client.get("/clients")
    assert r.status_code == 200
    assert len(r.json()) >= 1

    r = client.put(f"/clients/{cid}", json={"saldo_cc": 250.0})
    assert r.status_code == 200
    assert r.json()["saldo_cc"] == 250.0

    r = client.delete(f"/clients/{cid}")
    assert r.status_code == 204


def test_gateway_not_found():
    assert client.get("/clients/9999").status_code == 404
    assert client.put("/clients/9999", json={"nome":"x"}).status_code == 404
    assert client.delete("/clients/9999").status_code == 404


def test_index_fallback_when_no_static_file():
    """Testa fallback message quando index.html não existe (temporariamente)."""
    static_file = Path(__file__).parent.parent.parent.parent / "gateway" / "static" / "index.html"
    backup_file = static_file.parent / "index.html.backup"
    
    # Backup temporário
    if static_file.exists():
        shutil.move(str(static_file), str(backup_file))
    
    try:
        # Recriar cliente para forçar reload
        test_client = TestClient(app)
        r = test_client.get("/")
        assert r.status_code == 200
        data = r.json()
        assert "message" in data
        assert "Frontend" in data["message"]
    finally:
        # Restaurar arquivo
        if backup_file.exists():
            shutil.move(str(backup_file), str(static_file))
