import os
from pathlib import Path
from fastapi.testclient import TestClient

os.environ["JDBC_URL"] = "jdbc:h2:mem:end2end_db;DB_CLOSE_DELAY=-1"
local_jar = Path("app/storage/h2/h2.jar")
os.environ.setdefault("H2_JAR_PATH", str(local_jar if local_jar.exists() else "/opt/h2/h2.jar"))

from storage.main import app
from storage.db import init_db

client = TestClient(app)


def setup_module(_):
    init_db()


def test_end2end_flow_and_errors():
    r = client.get("/clients/999999")
    assert r.status_code == 404

    r = client.post("/clients", json={"nome": "", "telefone": 1, "correntista": True})
    assert r.status_code == 422

    r = client.post("/clients", json={"nome": "E2E", "telefone": 55, "correntista": False})
    assert r.status_code == 201
    cid = r.json()["id"]

    r = client.put("/clients/999999", json={"nome": "X"})
    assert r.status_code == 404

    r = client.delete(f"/clients/{cid}")
    assert r.status_code == 204
