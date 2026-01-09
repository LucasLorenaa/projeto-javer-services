from fastapi.testclient import TestClient
import gateway.client as gw_client
from gateway import main as gw_main


class FakeResponse:
    def __init__(self, data, status=200):
        self._data = data
        self.status_code = status

    def json(self):
        return self._data

    def raise_for_status(self):
        if self.status_code >= 400:
            import httpx
            raise httpx.HTTPStatusError(
                f"HTTP {self.status_code}",
                request=None,
                response=self
            )


class FakeHTTPClient:
    def __init__(self):
        self.db = {}
        self.next_id = 1

    def get(self, path):
        if path == "/clients":
            return FakeResponse(list(self.db.values()), 200)
        if path.startswith("/clients/"):
            cid = int(path.split("/")[-1])
            if cid in self.db:
                return FakeResponse(self.db[cid], 200)
            return FakeResponse({"detail": "Cliente não encontrado"}, 404)
        return FakeResponse({}, 404)

    def post(self, path, json=None):
        if path == "/clients":
            cid = self.next_id
            self.next_id += 1
            obj = {"id": cid, **(json or {})}
            self.db[cid] = obj
            return FakeResponse(obj, 201)
        return FakeResponse({}, 404)

    def put(self, path, json=None):
        if path.startswith("/clients/"):
            cid = int(path.split("/")[-1])
            if cid not in self.db:
                return FakeResponse({"detail": "Cliente não encontrado"}, 404)
            merged = {**self.db[cid], **{k: v for k, v in (json or {}).items() if v is not None}}
            self.db[cid] = merged
            return FakeResponse(merged, 200)
        return FakeResponse({}, 404)

    def delete(self, path):
        if path.startswith("/clients/"):
            cid = int(path.split("/")[-1])
            if cid not in self.db:
                return FakeResponse({"detail": "Cliente não encontrado"}, 404)
            del self.db[cid]
            return FakeResponse(None, 204)
        return FakeResponse({}, 404)


def setup_function():
    # injetar factory de cliente fake
    fake = FakeHTTPClient()
    gw_client.get_http_client = lambda: fake


def test_gateway_crud_and_score():
    client = TestClient(gw_main.app)

    # list initially empty
    r = client.get("/clients")
    assert r.status_code == 200
    assert r.json() == []

    # create client
    payload = {"nome": "T", "telefone": 1, "correntista": True}
    r = client.post("/clients", json=payload)
    assert r.status_code == 201
    created = r.json()
    cid = created["id"]

    # get client
    r = client.get(f"/clients/{cid}")
    assert r.status_code == 200

    # score sem saldo -> score_calculado é None
    r = client.get(f"/clients/{cid}/score")
    assert r.status_code == 200
    assert r.json()["score_calculado"] is None

    # atualizar cliente com saldo
    r = client.put(f"/clients/{cid}", json={"saldo_cc": 500.0})
    assert r.status_code == 200
    assert r.json()["saldo_cc"] == 500.0

    # score now computed
    r = client.get(f"/clients/{cid}/score")
    assert r.status_code == 200
    assert r.json()["score_calculado"] == 50.0

    # delete client
    r = client.delete(f"/clients/{cid}")
    assert r.status_code == 204

    # get should return 404
    r = client.get(f"/clients/{cid}")
    assert r.status_code == 404


def test_gateway_update_not_found():
    """Testa atualização de cliente inexistente"""
    client = TestClient(gw_main.app)
    r = client.put("/clients/999", json={"nome": "X"})
    assert r.status_code == 404


def test_gateway_delete_not_found():
    """Testa deleção de cliente inexistente"""
    client = TestClient(gw_main.app)
    r = client.delete("/clients/999")
    assert r.status_code == 404


def test_gateway_score_not_found():
    """Testa score de cliente inexistente"""
    client = TestClient(gw_main.app)
    r = client.get("/clients/999/score")
    assert r.status_code == 404
