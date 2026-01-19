import os
import psycopg2
from psycopg2 import sql

# Configurações PostgreSQL
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "javer_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")


def get_connection():
    """
    Retorna uma conexão PostgreSQL.
    Para testes em memória, usa sqlite3 como fallback.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
        )
        # Evita transações abortadas por erros de sintaxe no fallback de placeholders
        conn.autocommit = True
        return conn
    except psycopg2.OperationalError:
        # Fallback para testes: sqlite in-memory
        import sqlite3
        if not hasattr(get_connection, "_test_cache"):
            get_connection._test_cache = sqlite3.connect(":memory:", check_same_thread=False)
        return get_connection._test_cache


def init_db():
    """
    Cria a tabela 'clients' se não existir.
    """
    conn = get_connection()
    cur = conn.cursor()
    # Se estivermos no fallback sqlite (apenas testes), usa dialeto específico
    import sqlite3

    if isinstance(conn, sqlite3.Connection):
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone INTEGER UNIQUE,
                email TEXT UNIQUE,
                data_nascimento DATE,
                correntista INTEGER,
                score_credito REAL,
                saldo_cc REAL,
                senha_hash TEXT
            )
            """
        )
        conn.commit()
        return

    # SQL padrão PostgreSQL
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            id SERIAL PRIMARY KEY,
            nome VARCHAR(255) NOT NULL,
            telefone BIGINT UNIQUE,
            email VARCHAR(255) UNIQUE,
            data_nascimento DATE,
            correntista BOOLEAN,
            score_credito DOUBLE PRECISION,
            saldo_cc DOUBLE PRECISION,
            senha_hash VARCHAR(255)
        )
        """
    )
    cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS email VARCHAR(255) UNIQUE")
    cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS data_nascimento DATE")
    cur.execute("ALTER TABLE clients ADD COLUMN IF NOT EXISTS senha_hash VARCHAR(255)")
    # Remover coluna de idade se existir (migrando para data_nascimento)
    try:
        cur.execute("ALTER TABLE clients DROP COLUMN IF EXISTS idade")
    except:
        pass

    # Remove duplicados para permitir criação das constraints de unicidade
    cur.execute(
        """
        DELETE FROM clients a
        USING clients b
        WHERE a.id > b.id
          AND a.telefone IS NOT NULL
          AND b.telefone IS NOT NULL
          AND a.telefone = b.telefone;
        """
    )
    cur.execute(
        """
        DELETE FROM clients a
        USING clients b
        WHERE a.id > b.id
          AND a.email IS NOT NULL
          AND b.email IS NOT NULL
          AND a.email = b.email;
        """
    )

    # Adiciona constraints únicas somente se ainda não existirem
    cur.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'clients_telefone_key'
            ) THEN
                ALTER TABLE clients ADD CONSTRAINT clients_telefone_key UNIQUE (telefone);
            END IF;
        END$$;
        """
    )
    cur.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint WHERE conname = 'clients_email_key'
            ) THEN
                ALTER TABLE clients ADD CONSTRAINT clients_email_key UNIQUE (email);
            END IF;
        END$$;
        """
    )
    conn.commit()

