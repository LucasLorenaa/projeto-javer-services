from fastapi.testclient import TestClient
from gateway.main import app

client = TestClient(app)

def test_score_ok():
    r = client.post("/clients", json={"nome":"Score","telefone":1,"correntista":True,"saldo_cc":500.0})
    assert r.status_code == 201
    cid = r.json()["id"]

    r = client.get(f"/clients/{cid}/score")
    assert r.status_code == 200
    body = r.json()
    assert body["score_calculado"] == 50.0


def test_score_not_found():
    assert client.get("/clients/99999/score").status_code == 404
