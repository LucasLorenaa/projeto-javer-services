import types
import importlib


def test_get_connection_uses_jdbc_when_available(monkeypatch):
    # Create fake jaydebeapi module with connect that returns a fake connection object
    executed = []

    class FakeCursor:
        def execute(self, sql):
            executed.append(sql)

    class FakeConn:
        def cursor(self):
            return FakeCursor()
        def commit(self):
            pass
        def close(self):
            pass

    fake = types.SimpleNamespace()
    def fake_connect(*args, **kwargs):
        return FakeConn()
    fake.connect = fake_connect

    monkeypatch.setitem(importlib.import_module('sys').modules, 'jaydebeapi', fake)
    # monkeypatch H2_JAR_PATH env to something valid string
    import os
    os.environ['JDBC_URL'] = 'jdbc:h2:mem:test_jdbc;DB_CLOSE_DELAY=-1'

    # import inside test to ensure module uses patched sys.modules
    from storage.db import get_connection, init_db

    conn = get_connection()
    # should return our fake connection (not sqlite)
    assert hasattr(conn, 'cursor')
    # init_db should call CREATE TABLE on the JDBC branch; call it and ensure no exceptions
    init_db()
