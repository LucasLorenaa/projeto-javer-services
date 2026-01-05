import sqlite3
import pytest

from storage import repository as repo


def _make_conn_with_table():
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
    conn.commit()
    return conn


def test_get_client_closes_non_cached(monkeypatch):
    conn = _make_conn_with_table()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)",
        ("A", 0, True, None, None),
    )
    conn.commit()

    monkeypatch.setattr(repo, "get_connection", lambda: conn)
    res = repo.get_client(1)
    assert res is not None
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


def test_create_client_closes_non_cached(monkeypatch):
    conn = _make_conn_with_table()
    monkeypatch.setattr(repo, "get_connection", lambda: conn)
    created = repo.create_client({
        "nome": "C",
        "telefone": 0,
        "correntista": False,
    })
    assert created is not None
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


def test_update_client_closes_non_cached(monkeypatch):
    conn = _make_conn_with_table()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)",
        ("B", 0, True, None, None),
    )
    conn.commit()
    # avoid calling the real get_client which would close the connection used for the
    # existence check; stub it to return the expected current record
    monkeypatch.setattr(repo, "get_client", lambda _cid: {"id": 1, "nome": "B", "telefone": 0, "correntista": True, "score_credito": None, "saldo_cc": 0.0})
    monkeypatch.setattr(repo, "get_connection", lambda: conn)
    updated = repo.update_client(1, {"saldo_cc": 42.0})
    assert updated is not None
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")


def test_delete_client_closes_non_cached(monkeypatch):
    conn = _make_conn_with_table()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)",
        ("D", 0, True, None, None),
    )
    conn.commit()
    monkeypatch.setattr(repo, "get_connection", lambda: conn)
    ok = repo.delete_client(1)
    assert ok in (True, False)
    with pytest.raises(sqlite3.ProgrammingError):
        conn.execute("SELECT 1")
