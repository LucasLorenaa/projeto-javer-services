from fastapi.testclient import TestClient
from fastapi.testclient import TestClient
from gateway.main import app

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
