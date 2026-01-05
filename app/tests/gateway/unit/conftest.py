
# app/tests/gateway/unit/conftest.py
import sys
from pathlib import Path
import pytest

root = Path(__file__).resolve().parents[3]   # .../JAVER-SERVICES
app_dir = root / "app"
sys.path.insert(0, str(app_dir))

# Patch gateway.client at import time so tests that import gateway.main
# (during collection) will see the fake client. This ensures no real HTTP
# calls are attempted during collection or test execution.
try:
    import gateway.client as _gw_client
    _gw_client.get_http_client = lambda: None  # placeholder; fixture will override
except Exception:
    pass

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

    def post(self, path, json):
        if path == "/clients":
            cid = self.next_id
            self.next_id += 1
            obj = {"id": cid, **json}
            self.db[cid] = obj
            return FakeResponse(obj, 201)
        return FakeResponse({}, 404)

    def put(self, path, json):
        if path.startswith("/clients/"):
            cid = int(path.split("/")[-1])
            if cid not in self.db:
                return FakeResponse({"detail": "Cliente não encontrado"}, 404)
            merged = {**self.db[cid], **{k: v for k, v in json.items() if v is not None}}
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

class FakeResponse:
    def __init__(self, data, status):
        self._json = data
        self.status_code = status
    def json(self): return self._json
    def raise_for_status(self):
        if self.status_code >= 400:
            raise Exception(f"HTTP {self.status_code}")

@pytest.fixture(autouse=True)
def patch_gateway_http_client(monkeypatch):
    from gateway import client as gw_client
    # share a single FakeHTTPClient instance across requests so state (created clients)
    # is preserved between calls during a test
    fake = FakeHTTPClient()
    monkeypatch.setattr(gw_client, "get_http_client", lambda: fake)
    # also patch gateway.main's wrapper if it's been imported
    try:
        from gateway import main as gw_main
        monkeypatch.setattr(gw_main, "get_dynamic_http_client", lambda: fake)
    except Exception:
        pass
    yield
