import os
import sqlite3
from typing import Optional

H2_JAR_PATH = os.getenv("H2_JAR_PATH", os.path.join(os.path.dirname(__file__), "h2", "h2.jar"))
JDBC_URL = os.getenv("JDBC_URL", "jdbc:h2:./data/javer.db;AUTO_SERVER=TRUE")
JDBC_USER = os.getenv("JDBC_USER", "sa")
JDBC_PASS = os.getenv("JDBC_PASS", "")


def _parse_jdbc_to_sqlite_path(jdbc_url: str) -> Optional[str]:
    # mapeia jdbc:h2:mem:name... -> sqlite in-memory compartilhado usando URI (persistente entre conexões)
    if jdbc_url.startswith("jdbc:h2:mem:"):
        # extrai o nome após jdbc:h2:mem:
        rest = jdbc_url[len("jdbc:h2:mem:"):]
        name = rest.split(";")[0] or "javer_shared"
        # usa URI in-memory compartilhada do SQLite para permitir múltiplas conexões ao mesmo DB em memória
        return f"file:{name}?mode=memory&cache=shared"
    # jdbc:h2:/srv/data/javer.db;AUTO_SERVER=TRUE -> /srv/data/javer.db
    if jdbc_url.startswith("jdbc:h2:"):
        path_with_opts = jdbc_url[len("jdbc:h2:"):]
        path = path_with_opts.split(";")[0]
        # se o caminho é relativo, usa o caminho do workspace
        if path.startswith("/") or ":\\" in path:
            return path + ".sqlite"
        return os.path.join(os.getcwd(), path + ".sqlite")
    return None


def get_connection():
    """
    Tenta retornar uma conexão JDBC via jaydebeapi/H2; se indisponível, usa sqlite3 como fallback.
    """
    try:
        import jaydebeapi

        # tenta conectar usando H2
        return jaydebeapi.connect(
            "org.h2.Driver",
            JDBC_URL,
            [JDBC_USER, JDBC_PASS],
            jars=H2_JAR_PATH,
        )
    except Exception:
        # fallback para sqlite3
        sqlite_path = _parse_jdbc_to_sqlite_path(JDBC_URL) or os.path.join(os.getcwd(), "javer_fallback.sqlite")
        # Usa uma conexão em cache por sqlite_path para que as tabelas persistam entre chamadas (importante para testes)
        if not hasattr(get_connection, "_sqlite_cache"):
            get_connection._sqlite_cache = {}
        cache = get_connection._sqlite_cache
        if sqlite_path in cache:
            return cache[sqlite_path]
        # Se sqlite_path é uma URI (começa com file:), passa uri=True para que o SQLite interprete corretamente
        if isinstance(sqlite_path, str) and sqlite_path.startswith("file:"):
            conn = sqlite3.connect(sqlite_path, check_same_thread=False, uri=True)
        else:
            conn = sqlite3.connect(sqlite_path, check_same_thread=False)
        cache[sqlite_path] = conn
        return conn


def init_db():
    conn = get_connection()
    try:
        cur = conn.cursor()
        # Usa SQL compatível com H2 e SQLite quando possível; ramifica se for sqlite
        is_sqlite = isinstance(conn, sqlite3.Connection)
        if is_sqlite:
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
        else:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS clients (
                    id IDENTITY PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    telefone BIGINT,
                    correntista BOOLEAN,
                    score_credito DOUBLE,
                    saldo_cc DOUBLE
                )
                """
            )
        conn.commit()
    finally:
        # Não fecha conexões sqlite aqui porque podem estar em cache/compartilhadas para testes
        try:
            import sqlite3 as _sqlite
            if not isinstance(conn, _sqlite.Connection):
                conn.close()
        except Exception:
            try:
                conn.close()
            except Exception:
                pass
