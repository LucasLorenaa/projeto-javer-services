import hashlib
import sqlite3
from unittest.mock import patch

import pytest

from storage import db
from storage import repository as repo


@pytest.fixture(autouse=True)
def force_sqlite(monkeypatch):
    """Ensure tests use sqlite fallback and start with clean tables."""
    if hasattr(db.get_connection, "_test_cache"):
        del db.get_connection._test_cache
    def _raise_operational_error(*args, **kwargs):
        raise db.psycopg2.OperationalError("fail")
    monkeypatch.setattr(db.psycopg2, "connect", _raise_operational_error)
    conn = db.get_connection()
    conn.execute("DELETE FROM investments")
    conn.execute("DELETE FROM clients")
    conn.commit()
    yield conn
    conn.execute("DELETE FROM investments")
    conn.execute("DELETE FROM clients")
    conn.commit()
    if hasattr(db.get_connection, "_test_cache"):
        del db.get_connection._test_cache


def test_get_connection_creates_schema(force_sqlite):
    conn = db.get_connection()
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('clients','investments')")
    tables = {row[0] for row in cur.fetchall()}
    assert {"clients", "investments"}.issubset(tables)


def test_init_db_postgres_branch(monkeypatch):
    class FakeCursor:
        def __init__(self):
            self.executed = []
        def execute(self, query, params=None):
            self.executed.append((query, params))
        def fetchone(self):
            return None
    class FakeConn:
        def __init__(self):
            self.cursor_obj = FakeCursor()
            self.autocommit = False
            self.committed = False
        def cursor(self):
            return self.cursor_obj
        def commit(self):
            self.committed = True
    fake_conn = FakeConn()
    if hasattr(db.get_connection, "_test_cache"):
        del db.get_connection._test_cache
    monkeypatch.setattr(db.psycopg2, "connect", lambda **kwargs: fake_conn)

    db.init_db()

    assert fake_conn.cursor_obj.executed  # several statements executed
    assert fake_conn.committed is True


def test_create_investments_table_postgres(monkeypatch):
    class FakeCursor:
        def __init__(self):
            self.executed = []
        def execute(self, query, params=None):
            self.executed.append((query, params))
    class FakeConn:
        def __init__(self):
            self.cursor_obj = FakeCursor()
            self.committed = False
            self.autocommit = False
        def cursor(self):
            return self.cursor_obj
        def commit(self):
            self.committed = True
    fake_conn = FakeConn()
    if hasattr(db.get_connection, "_test_cache"):
        del db.get_connection._test_cache
    monkeypatch.setattr(db.psycopg2, "connect", lambda **kwargs: fake_conn)

    db.create_investments_table()

    assert fake_conn.cursor_obj.executed
    assert fake_conn.committed is True


def test_validate_password_strength():
    with pytest.raises(ValueError):
        repo._validate_password_strength("123")
    with pytest.raises(ValueError):
        repo._validate_password_strength("password")
    repo._validate_password_strength("Senha@123")  # should not raise


def test_is_password_pwned_branches(monkeypatch):
    pwd = "senhaSegura"
    sha1 = hashlib.sha1(pwd.encode("utf-8")).hexdigest().upper()
    prefix, suffix = sha1[:5], sha1[5:]

    class Resp:
        def __init__(self, status_code, text):
            self.status_code = status_code
            self.text = text
    # Found in dataset
    monkeypatch.setattr(repo.requests, "get", lambda url, timeout: Resp(200, f"{suffix}:5\nOTHER:1"))
    assert repo._is_password_pwned(pwd) is True

    # Non-200 status -> False
    monkeypatch.setattr(repo.requests, "get", lambda url, timeout: Resp(503, ""))
    assert repo._is_password_pwned(pwd) is False

    # Exception path -> False
    def boom(url, timeout):
        raise RuntimeError("net down")
    monkeypatch.setattr(repo.requests, "get", boom)
    assert repo._is_password_pwned(pwd) is False


def test_execute_query_branches(monkeypatch):
    class FallbackCursor:
        def __init__(self):
            self.calls = 0
        def execute(self, query, params=None):
            self.calls += 1
            if self.calls == 1:
                raise Exception("syntax error near ?")
            return "ok"
    class FallbackConn(sqlite3.Connection):
        def cursor(self):
            return FallbackCursor()
    conn = sqlite3.connect(":memory:", factory=FallbackConn)
    cur = conn.cursor()
    repo._execute_query(conn, cur, "BAD ?", "SELECT 1", ())
    assert cur.calls == 2

    class PgCursor:
        def __init__(self):
            self.received = None
        def execute(self, query, params=None):
            self.received = (query, params)
    class PgConn:
        def cursor(self):
            return PgCursor()
    pg_conn = PgConn()
    pg_cur = pg_conn.cursor()
    repo._execute_query(pg_conn, pg_cur, "SELECT 1", "SELECT 2", (1,))
    assert pg_cur.received == ("SELECT 2", (1,))


def test_row_helpers_and_cache(force_sqlite):
    # Insert directly to check row transformation
    conn = force_sqlite
    conn.execute("INSERT INTO clients (nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?, ?, ?)",
                 ("Joao", 123456789, "j@test.com", "2000-01-01", 1, None, 200.0))
    conn.commit()
    cur = conn.cursor()
    cur.execute("SELECT id, nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc FROM clients")
    row = cur.fetchone()
    client = repo._row_to_client(row)
    assert client["score_credito"] == pytest.approx(20.0)

    # _should_close_connection returns False for cached connection
    db.get_connection._test_cache = conn
    assert repo._should_close_connection(conn) is False


def test_ensure_unique_validation(force_sqlite):
    conn = force_sqlite
    conn.execute("INSERT INTO clients (nome, telefone, email) VALUES (?, ?, ?)", ("Joao", 111, "joao@test.com"))
    conn.commit()
    with pytest.raises(ValueError):
        repo._ensure_unique(conn, "joao@test.com", 222)
    # Excluding same id should pass
    repo._ensure_unique(conn, "joao@test.com", 111, exclude_id=1)


@patch("storage.repository._is_password_pwned", return_value=False)
def test_create_update_login_delete_flow(mock_pwned, force_sqlite):
    conn = force_sqlite
    data = {
        "nome": "Maria",
        "telefone": 999,
        "email": "maria@test.com",
        "data_nascimento": "1990-01-01",
        "correntista": True,
        "score_credito": 10.0,
        "saldo_cc": 500.0,
        "senha": "Senha@123",
    }
    created = repo.create_client(data)
    assert created is not None
    updated = repo.update_client(created["id"], {"nome": "Maria Atualizada", "senha": "NovaSenha@123"})
    assert updated["nome"] == "Maria Atualizada"

    assert repo.login_client(data["email"], "NovaSenha@123") is not None
    assert repo.login_client(data["email"], "errada") is None

    assert repo.update_password(data["email"], "SenhaMaisForte@123") is True
    assert repo.delete_client(created["id"]) is True


def test_create_client_password_pwned(force_sqlite, monkeypatch):
    monkeypatch.setattr(repo, "_is_password_pwned", lambda pwd: True)
    with pytest.raises(ValueError):
        repo.create_client({
            "nome": "Ana",
            "telefone": 1234,
            "email": "ana@test.com",
            "data_nascimento": "1999-01-01",
            "correntista": False,
            "score_credito": None,
            "saldo_cc": 0.0,
            "senha": "Senha@123",
        })


def test_update_password_validation(force_sqlite, monkeypatch):
    monkeypatch.setattr(repo, "_is_password_pwned", lambda pwd: False)

    # Create client without senha to set hash later
    repo.create_client({
        "nome": "Carlos",
        "telefone": 555,
        "email": "carlos@test.com",
        "data_nascimento": "1995-01-01",
        "correntista": True,
        "score_credito": None,
        "saldo_cc": 0.0,
        "senha": "Senha@123",
    })
    with pytest.raises(ValueError):
        repo.update_password("carlos@test.com", "123")
    assert repo.update_password("inexistente@test.com", "Senha@123") is False


def test_delete_client_missing(force_sqlite):
    assert repo.delete_client(9999) is False
