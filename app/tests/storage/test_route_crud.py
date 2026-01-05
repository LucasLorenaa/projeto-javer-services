import os
from pathlib import Path
from fastapi.testclient import TestClient

os.environ["JDBC_URL"] = "jdbc:h2:mem:routes_db;DB_CLOSE_DELAY=-1"
local_jar = Path("app/storage/h2/h2.jar")
os.environ.setdefault("H2_JAR_PATH", str(local_jar if local_jar.exists() else "/opt/h2/h2.jar"))

from storage.main import app
from storage.db import init_db

client = TestClient(app)


def setup_module(_):
    init_db()


def test_routes_crud():
    payload = {
        "nome": "API Test",
        "telefone": 21911111111,
        "correntista": True,
        "score_credito": 600.0,
        "saldo_cc": 2000.0
    }
    r = client.post("/clients", json=payload)
    assert r.status_code == 201
    cid = r.json()["id"]

    r = client.get(f"/clients/{cid}")
    assert r.status_code == 200
    assert r.json()["nome"] == "API Test"

    r = client.get("/clients")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.put(f"/clients/{cid}", json={"saldo_cc": 3000.0})
    assert r.status_code == 200
    assert r.json()["saldo_cc"] == 3000.0

    r = client.delete(f"/clients/{cid}")
    assert r.status_code == 204

    r = client.get(f"/clients/{cid}")
    assert r.status_code == 404
