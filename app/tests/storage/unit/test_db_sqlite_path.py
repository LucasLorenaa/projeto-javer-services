import os
import sqlite3
from pathlib import Path
import pytest

# Configura variável de ambiente antes de importar storage.db
os.environ["JDBC_URL"] = "jdbc:h2:./testdata/test.db"
local_jar = Path("app/storage/h2/h2.jar")
os.environ.setdefault("H2_JAR_PATH", str(local_jar if local_jar.exists() else "/opt/h2/h2.jar"))

from storage import db as storage_db


def test_sqlite_connection_non_uri_path():
    """Testa o caminho else do sqlite onde não é URI (linha 57)"""
    # Força o uso do caminho não-URI
    original_parse = storage_db._parse_jdbc_to_sqlite_path
    
    def mock_parse(url):
        # Retorna um caminho que não começa com "file:"
        return "./test_regular.sqlite"
    
    storage_db._parse_jdbc_to_sqlite_path = mock_parse
    
    # Limpa o cache se existir
    if hasattr(storage_db.get_connection, "_sqlite_cache"):
        storage_db.get_connection._sqlite_cache.clear()
    
    try:
        conn = storage_db.get_connection()
        assert isinstance(conn, sqlite3.Connection)
        
        # Verifica que a conexão funciona
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        assert result[0] == 1
    finally:
        storage_db._parse_jdbc_to_sqlite_path = original_parse
        # Limpa o arquivo de teste
        if os.path.exists("./test_regular.sqlite"):
            try:
                os.remove("./test_regular.sqlite")
            except Exception:
                pass
