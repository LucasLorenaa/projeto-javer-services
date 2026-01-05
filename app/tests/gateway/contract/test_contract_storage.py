import os
import shutil
import pytest
from fastapi.testclient import TestClient

has_java = shutil.which("java") is not None
h2_jar_exists = os.path.exists("app/storage/h2/h2.jar")
pytestmark = pytest.mark.skipif(
    not (has_java and h2_jar_exists),
    reason="Contrato depende de Java + h2.jar. Rode via Dockerfile.tests ou instale Java."
)

os.environ["JDBC_URL"] = "jdbc:h2:mem:contract_db;DB_CLOSE_DELAY=-1"
os.environ.setdefault("H2_JAR_PATH", "app/storage/h2/h2.jar")

from storage.main import app as storage_app
from storage.db import init_db
from gateway.main import app as gateway_app

storage_client = TestClient(storage_app)


def setup_module(_):
    init_db()


def test_gateway_contract(monkeypatch):
    class TCAdapterClient:
        def get(self, path): return _convert(storage_client.get(path))
        def post(self, path, json=None): return _convert(storage_client.post(path, json=json))
        def put(self, path, json=None): return _convert(storage_client.put(path, json=json))
        def delete(self, path): return _convert(storage_client.delete(path))

    class RespProxy:
        def __init__(self, r):
            self.status_code = r.status_code
            self._json = r.json() if getattr(r, 'content', None) else None
        def json(self): return self._json
        def raise_for_status(self):
            if self.status_code >= 400: raise Exception(f"HTTP {self.status_code}")

    def _convert(r): return RespProxy(r)

    from gateway import client as gw_client
    monkeypatch.setattr(gw_client, "get_http_client", lambda: TCAdapterClient())

    gw = TestClient(gateway_app)

    r = gw.post("/clients", json={"nome":"CT","telefone":1,"correntista":True,"saldo_cc":1000.0})
    assert r.status_code == 201
    cid = r.json()["id"]

    r = gw.get(f"/clients/{cid}/score")
    assert r.status_code == 200
    assert r.json()["score_calculado"] == 100.0

    r = gw.get(f"/clients/{cid}")
    body = r.json()
    for field in ("id","nome","telefone","correntista","score_credito","saldo_cc"):
        assert field in body
