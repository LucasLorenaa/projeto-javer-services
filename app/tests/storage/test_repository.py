import os
from pathlib import Path

os.environ["JDBC_URL"] = "jdbc:h2:mem:repo_db;DB_CLOSE_DELAY=-1"
local_jar = Path("app/storage/h2/h2.jar")
os.environ.setdefault("H2_JAR_PATH", str(local_jar if local_jar.exists() else "/opt/h2/h2.jar"))

from storage.db import init_db
from storage.repository import create_client, list_clients, get_client, update_client, delete_client


def setup_module(_):
    init_db()


def test_repository_crud_cycle():
    created = create_client({
        "nome": "Repo Test",
        "telefone": 21900000000,
        "correntista": True,
        "score_credito": 700.0,
        "saldo_cc": 1000.0
    })
    assert created["id"] > 0

    c = get_client(created["id"])
    assert c["nome"] == "Repo Test"

    lst = list_clients()
    assert len(lst) >= 1

    updated = update_client(created["id"], {"saldo_cc": 5000.0})
    assert updated["saldo_cc"] == 5000.0

    ok = delete_client(created["id"])
    assert ok is True
    assert get_client(created["id"]) is None
