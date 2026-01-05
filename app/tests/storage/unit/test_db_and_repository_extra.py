import os
import sqlite3
import types
from pathlib import Path

import pytest

# Ensure JDBC_URL uses an in-memory H2-style URI so the DB fallback maps to a shared
# sqlite in-memory DB for tests (avoids creating files on disk)
os.environ["JDBC_URL"] = "jdbc:h2:mem:extra_db;DB_CLOSE_DELAY=-1"
local_jar = Path("app/storage/h2/h2.jar")
os.environ.setdefault("H2_JAR_PATH", str(local_jar if local_jar.exists() else "/opt/h2/h2.jar"))

from storage import main as storage_main
from storage import db as storage_db
from storage import repository as storage_repo


def test_health_and_delete_not_found():
    from fastapi.testclient import TestClient
    # ensure DB initialized for the app routes
    storage_db.init_db()
    client = TestClient(storage_main.app)

    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["service"] == "storage"

    # deleting a non-existent client should return 404
    r = client.delete("/clients/999999")
    assert r.status_code == 404


def test_startup_event_calls_init_db(monkeypatch):
    called = {"v": False}

    def fake_init():
        called["v"] = True

    # storage.main imported init_db at import time, patch that symbol instead
    monkeypatch.setattr(storage_main, "init_db", fake_init)
    # call the lifespan startup code directly
    import asyncio
    async def run_lifespan():
        async with storage_main.lifespan(storage_main.app):
            pass
    asyncio.run(run_lifespan())
    assert called["v"] is True


def test_init_db_closes_non_sqlite_connection(monkeypatch):
    # create a fake connection object that is NOT a sqlite3.Connection
    closed = {"v": False}

    class FakeCur:
        def execute(self, *a, **k):
            return None

    class FakeConn:
        def cursor(self):
            return FakeCur()

        def commit(self):
            return None

        def close(self):
            closed["v"] = True

    monkeypatch.setattr(storage_db, "get_connection", lambda: FakeConn())
    # should call close() on non-sqlite connection
    storage_db.init_db()
    assert closed["v"] is True


def test_init_db_close_raises(monkeypatch):
    # simulate a connection whose close() raises an exception to hit the nested except
    class FakeConnRaise:
        def cursor(self):
            class C:
                def execute(self, *a, **k):
                    return None
            return C()

        def commit(self):
            return None

        def close(self):
            raise RuntimeError("close failed")

    monkeypatch.setattr(storage_db, "get_connection", lambda: FakeConnRaise())
    # should not raise even if close fails
    storage_db.init_db()


def test_repository_closes_non_cached_sqlite_conn(monkeypatch):
    # create a dedicated in-memory sqlite connection (not in any cache)
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone INTEGER,
            correntista BOOLEAN,
            score_credito REAL,
            saldo_cc REAL
        )
        """
    )
    cur.execute(
        "INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)",
        ("X", 0, True, 100.0, 10.0),
    )
    conn.commit()

    # monkeypatch repository.get_connection to return this conn (not cached)
    monkeypatch.setattr(storage_repo, "get_connection", lambda: conn)

    # call list_clients(), which should close the connection afterwards
    res = storage_repo.list_clients()
    assert isinstance(res, list)

    # after the call the connection should be closed; operations should raise
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
