import os
import sqlite3

H2_JAR_PATH = os.getenv("H2_JAR_PATH", os.path.join(os.path.dirname(__file__), "h2", "h2.jar"))
JDBC_URL = os.getenv("JDBC_URL", "jdbc:h2:./data/javer.db;AUTO_SERVER=TRUE")
JDBC_USER = os.getenv("JDBC_USER", "sa")
JDBC_PASS = os.getenv("JDBC_PASS", "")


def get_connection():
    """
    Retorna uma conexão JDBC via jaydebeapi/H2.
    Para testes, usa sqlite3 em memória como fallback.
    """
    try:
        import jaydebeapi
        return jaydebeapi.connect(
            "org.h2.Driver",
            JDBC_URL,
            [JDBC_USER, JDBC_PASS],
            jars=H2_JAR_PATH,
        )
    except Exception:
        # Fallback para testes: sqlite in-memory
        if "mem:" in JDBC_URL:
            if not hasattr(get_connection, "_test_cache"):
                get_connection._test_cache = sqlite3.connect(":memory:", check_same_thread=False)
            return get_connection._test_cache
        raise


def init_db():
    """
    Cria a tabela 'clients' se não existir.
    """
    conn = get_connection()
    cur = conn.cursor()
    try:
        # Tenta SQL do H2
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id IDENTITY PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                telefone BIGINT,
                correntista BOOLEAN,
                score_credito DOUBLE,
                saldo_cc DOUBLE
            )
        """)
    except Exception:
        # Fallback para SQLite (só para testes)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone INTEGER,
                correntista INTEGER,
                score_credito REAL,
                saldo_cc REAL
            )
        """)
    conn.commit()

