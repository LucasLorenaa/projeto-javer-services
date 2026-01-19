"""Configurações e fixtures para os testes"""
import pytest
import os


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Inicializa o banco de dados de teste"""
    # Garantir que usamos sqlite para testes
    os.environ.pop("DB_HOST", None)
    
    # Importar init_db e inicializar
    from storage.db import init_db
    init_db()
    yield


@pytest.fixture(autouse=True)
def clean_db():
    """Limpa o banco entre os testes"""
    from storage.repository import get_connection
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM clients")
        conn.commit()
    except Exception:
        pass
    yield


@pytest.fixture(autouse=True)
def override_gateway_client():
    """Garante cliente HTTP fake para o gateway em todos os testes."""
    try:
        from gateway import main as gw_main

        class _DummyResponse:
            def __init__(self, data, status):
                self._data = data
                self.status_code = status
            def json(self):
                return self._data
            def raise_for_status(self):
                if self.status_code >= 400:
                    raise Exception(f"HTTP {self.status_code}")

        class _DummyClient:
            def __init__(self):
                self.db = {
                    1: {"id": 1, "nome": "João", "email": "joao@test.com", "telefone": 123456789, "correntista": True, "data_nascimento": "2000-01-01", "score_credito": None, "saldo_cc": 0},
                    2: {"id": 2, "nome": "Maria", "email": "maria@test.com", "telefone": 987654321, "correntista": False, "data_nascimento": "2000-01-02", "score_credito": None, "saldo_cc": 0},
                }
                self.next_id = 3
            def get(self, path):
                if path == "/clients":
                    return _DummyResponse(list(self.db.values()), 200)
                if path.startswith("/clients/"):
                    cid = int(path.split("/")[-1])
                    if cid in self.db:
                        return _DummyResponse(self.db[cid], 200)
                    return _DummyResponse({"detail": "Cliente não encontrado"}, 404)
                return _DummyResponse({}, 404)
            def post(self, path, json):
                if path in ["/clients", "/register"]:
                    cid = self.next_id
                    self.next_id += 1
                    obj = {
                        "id": cid,
                        "telefone": json.get("telefone", 0),
                        "correntista": json.get("correntista", True),
                        "score_credito": json.get("score_credito"),
                        "saldo_cc": json.get("saldo_cc", 0),
                        **json,
                    }
                    self.db[cid] = obj
                    return _DummyResponse(obj, 201)
                if path == "/login":
                    return _DummyResponse({"id": 1, **json}, 200)
                return _DummyResponse({}, 404)
            def put(self, path, json):
                if path.startswith("/clients/"):
                    cid = int(path.split("/")[-1])
                    if cid not in self.db:
                        return _DummyResponse({"detail": "Cliente não encontrado"}, 404)
                    merged = {**self.db[cid], **{k: v for k, v in json.items() if v is not None}}
                    self.db[cid] = merged
                    return _DummyResponse(merged, 200)
                if path == "/password":
                    return _DummyResponse({"detail": "Senha atualizada"}, 200)
                return _DummyResponse({}, 404)
            def delete(self, path):
                if path.startswith("/clients/"):
                    cid = int(path.split("/")[-1])
                    if cid not in self.db:
                        return _DummyResponse({"detail": "Cliente não encontrado"}, 404)
                    self.db.pop(cid, None)
                    return _DummyResponse(None, 204)
                return _DummyResponse({}, 404)

        dummy = _DummyClient()
        dep_callable = gw_main.get_dynamic_http_client
        if dep_callable not in gw_main.app.dependency_overrides:
            gw_main.app.dependency_overrides[dep_callable] = lambda: (gw_main.get_dynamic_http_client() or dummy)
    except Exception:
        pass
    yield
    try:
        gw_main.app.dependency_overrides.pop(gw_main.get_dynamic_http_client, None)
    except Exception:
        pass
