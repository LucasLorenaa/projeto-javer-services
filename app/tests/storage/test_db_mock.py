from unittest.mock import patch, MagicMock
import pytest


def test_get_connection_h2_success():
    """Testa conexão H2 bem sucedida"""
    mock_jdbc = MagicMock()
    
    # Mockar jaydebeapi.connect
    with patch("jaydebeapi.connect", return_value=mock_jdbc):
        from storage.db import get_connection
        conn = get_connection()
        assert conn == mock_jdbc


def test_get_connection_fallback_to_sqlite():
    """Testa fallback para SQLite quando jaydebeapi falha"""
    import os
    os.environ["JDBC_URL"] = "jdbc:h2:mem:testfallback;DB_CLOSE_DELAY=-1"
    
    # Mockar o import para falhar
    import sys
    original_import = __builtins__['__import__']
    
    def mock_import(name, *args, **kwargs):
        if name == 'jaydebeapi':
            raise ImportError("No module named jaydebeapi")
        return original_import(name, *args, **kwargs)
    
    with patch('builtins.__import__', side_effect=mock_import):
        # Reimportar db para forçar fallback
        import importlib
        import storage.db
        importlib.reload(storage.db)
        
        conn = storage.db.get_connection()
        assert conn is not None


def test_init_db_creates_table_h2():
    """Testa que init_db cria tabela no H2"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    
    with patch("storage.db.get_connection", return_value=mock_conn):
        from storage.db import init_db
        init_db()
        
        # Verificar que cursor foi chamado
        mock_conn.cursor.assert_called_once()
        # Verificar que commit foi chamado
        mock_conn.commit.assert_called_once()


def test_init_db_fallback_to_sqlite_schema():
    """Testa que init_db tenta SQL do SQLite quando H2 falha"""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    # Primeira chamada execute falha (H2 SQL)
    # Segunda chamada execute funciona (SQLite SQL)
    mock_cursor.execute.side_effect = [Exception("H2 syntax error"), None]
    mock_conn.cursor.return_value = mock_cursor
    
    with patch("storage.db.get_connection", return_value=mock_conn):
        from storage.db import init_db
        init_db()
        
        # Verificar que execute foi chamado 2 vezes
        assert mock_cursor.execute.call_count == 2
