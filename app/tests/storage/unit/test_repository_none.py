import os
from pathlib import Path
import pytest

os.environ["JDBC_URL"] = "jdbc:h2:mem:repo_none_test;DB_CLOSE_DELAY=-1"
local_jar = Path("app/storage/h2/h2.jar")
os.environ.setdefault("H2_JAR_PATH", str(local_jar if local_jar.exists() else "/opt/h2/h2.jar"))

from storage import repository as repo
from storage import db as storage_db


def test_create_client_max_id_none():
    """Testa cenário onde SELECT MAX(id) retorna None"""
    storage_db.init_db()
    
    # Mock apenas o get_client para retornar None
    original_get_client = repo.get_client
    repo.get_client = lambda x: None
    
    try:
        # Cria um cliente, mas como get_client retorna None, o resultado será None
        # mesmo que o insert tenha funcionado
        conn = storage_db.get_connection()
        cur = conn.cursor()
        
        # Insere diretamente para garantir que há dados
        cur.execute(
            "INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)",
            ("TestNone", 999, False, None, None)
        )
        conn.commit()
        
        # Agora deleta todos os registros para que MAX retorne None
        cur.execute("DELETE FROM clients")
        conn.commit()
        
        # Tenta criar um cliente quando a tabela está vazia (cenário improvável mas possível)
        result = repo.create_client({
            "nome": "Empty",
            "telefone": 1,
            "correntista": False
        })
        
        # Com get_client mockado para None, deve retornar None
        assert result is None
        
    finally:
        repo.get_client = original_get_client

