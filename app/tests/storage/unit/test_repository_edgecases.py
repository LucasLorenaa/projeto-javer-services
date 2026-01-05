import os
import sqlite3
from pathlib import Path

os.environ["JDBC_URL"] = "jdbc:h2:mem:edge_db;DB_CLOSE_DELAY=-1"
local_jar = Path("app/storage/h2/h2.jar")
os.environ.setdefault("H2_JAR_PATH", str(local_jar if local_jar.exists() else "/opt/h2/h2.jar"))

from storage.db import init_db
from storage.repository import get_client, update_client, delete_client, create_client


def setup_module(_):
    init_db()


def test_get_client_none():
    assert get_client(9999999) is None


def test_update_client_not_found():
    assert update_client(9999999, {"saldo_cc": 1.0}) is None


def test_delete_client_not_found():
    assert delete_client(9999999) is False


def test_create_and_get_roundtrip():
    created = create_client({
        "nome": "Edge",
        "telefone": 0,
        "correntista": False,
        "score_credito": None,
        "saldo_cc": None,
    })
    assert created and created.get("id") is not None
    got = get_client(created["id"])
    assert got["nome"] == "Edge"
