from typing import List, Optional, Dict, Any
from .db import get_connection
import sqlite3
import bcrypt
import re
import hashlib
import requests


def _compute_score(saldo: Optional[float]) -> Optional[float]:
    """Calcula o score de crédito a partir do saldo, se disponível."""
    return (saldo * 0.1) if saldo is not None else None


def _hash_password(senha: str) -> str:
    """Hash de senha usando bcrypt."""
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()


def _verify_password(senha: str, senha_hash: str) -> bool:
    """Verifica se senha corresponde ao hash."""
    return bcrypt.checkpw(senha.encode(), senha_hash.encode())


def _validate_password_strength(senha: str):
    """Valida regras mínimas de senha.

    Regras:
    - Mínimo 6 caracteres
    - Recomendado: letra minúscula, maiúscula, dígito e símbolo (mas não obrigatório)
    """
    if len(senha) < 6:
        raise ValueError("Senha deve ter ao menos 6 caracteres")

    weak_list = {
        "123456", "123456789", "password", "qwerty", "abc123",
        "111111", "123123", "senha", "admin", "iloveyou"
    }
    if senha.lower() in weak_list:
        raise ValueError("Senha muito comum, escolha outra")



def _is_password_pwned(senha: str) -> bool:
    """Consulta HIBP Pwned Passwords via k-anonimidade. Retorna True se comprometida.
    Em erro de rede, não bloqueia (retorna False).
    """
    try:
        sha1 = hashlib.sha1(senha.encode("utf-8")).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        resp = requests.get(url, timeout=2)
        if resp.status_code != 200:
            return False
        lines = resp.text.splitlines()
        for line in lines:
            parts = line.split(":")
            if len(parts) != 2:
                continue
            suf, count = parts
            if suf.upper() == suffix:
                return int(count) > 0
        return False
    except Exception:
        # Falha de rede: não bloquear usuário
        return False


def _execute_query(conn, cur, query_sqlite: str, query_postgres: str, params: tuple):
    """Executa a query usando o dialeto correto conforme o driver.

    - Para conexões sqlite3: tenta primeiro query_sqlite (placeholders "?")
      e, se falhar por sintaxe, tenta query_postgres ("%s").
    - Para psycopg2 (PostgreSQL): executa direto query_postgres, evitando
      gerar erro de sintaxe com "?" que deixaria a transação abortada.
    """
    is_sqlite = isinstance(conn, sqlite3.Connection)

    if not is_sqlite:
        # Psycopg2: usa diretamente a sintaxe do PostgreSQL
        return cur.execute(query_postgres, params)  # pragma: no cover - caminho PostgreSQL

    # Caminho SQLite: tenta '?' e faz retorno alternativo para '%s' se necessário
    try:
        return cur.execute(query_sqlite, params)
    except Exception as e:
        if "near" in str(e) or "syntax" in str(e):
            return cur.execute(query_postgres, params)
        raise


def _row_to_client(row) -> Dict[str, Any]:
    saldo = float(row[7]) if row[7] is not None else None
    score = float(row[6]) if row[6] is not None else _compute_score(saldo)
    patrimonio_inv = float(row[8]) if len(row) > 8 and row[8] is not None else 0.0
    return {
        "id": row[0],
        "nome": row[1],
        "telefone": int(row[2]),
        "email": row[3],
        "data_nascimento": row[4],
        "correntista": bool(row[5]),
        "score_credito": score,
        "saldo_cc": saldo,
        "patrimonio_investimento": patrimonio_inv,
    }


def _should_close_connection(conn) -> bool:
    """Verifica se a conexão deve ser fechada (não está em cache)."""
    # Se a conexão não é a do cache, deve ser fechada
    if hasattr(get_connection, "_test_cache"):
        return conn is not get_connection._test_cache
    return True


def list_clients() -> List[Dict[str, Any]]:
    conn = get_connection()
    should_close = _should_close_connection(conn)
    try:
        cur = conn.cursor()
        _execute_query(
            conn,
            cur,
            "SELECT id, nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, patrimonio_investimento FROM clients",
            "SELECT id, nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, patrimonio_investimento FROM clients",
            ()
        )
        rows = cur.fetchall()
        return [_row_to_client(r) for r in rows]
    finally:
        if should_close:
            conn.close()


def get_client(client_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    should_close = _should_close_connection(conn)
    try:
        cur = conn.cursor()
        _execute_query(
            conn,
            cur,
            "SELECT id, nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, patrimonio_investimento FROM clients WHERE id = ?",
            "SELECT id, nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, patrimonio_investimento FROM clients WHERE id = %s",
            (client_id,)
        )
        row = cur.fetchone()
        return _row_to_client(row) if row else None
    finally:
        if should_close:
            conn.close()


def _ensure_unique(conn, email: str, telefone: int, exclude_id: Optional[int] = None):
    cur = conn.cursor()
    params = [email, telefone]
    query_sqlite = "SELECT id FROM clients WHERE (email = ? OR telefone = ?)"
    query_postgres = "SELECT id FROM clients WHERE (email = %s OR telefone = %s)"
    if exclude_id is not None:
        query_sqlite += " AND id <> ?"
        query_postgres += " AND id <> %s"
        params.append(exclude_id)
    _execute_query(conn, cur, query_sqlite, query_postgres, tuple(params))
    row = cur.fetchone()
    if row:
        raise ValueError("Email ou telefone já cadastrado")


def create_client(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    should_close = _should_close_connection(conn)
    try:
        cur = conn.cursor()
        _ensure_unique(conn, data["email"], data["telefone"])
        
        # Validar e gerar hash da senha se fornecida
        senha_hash = None
        if "senha" in data:
            _validate_password_strength(data["senha"])
            if _is_password_pwned(data["senha"]):
                raise ValueError("Senha comprometida em vazamentos. Escolha outra.")
            senha_hash = _hash_password(data["senha"])
        
        params_pg = (
            data["nome"],
            data["telefone"],
            data["email"],
            data["data_nascimento"],
            data["correntista"],
            data.get("score_credito"),
            data.get("saldo_cc"),
            senha_hash,
            data.get("patrimonio_investimento", 0.0),
        )
        params_sqlite = params_pg
        
        new_id = None
        
        # Tenta PostgreSQL com RETURNING
        try:
            cur.execute(  # pragma: no cover - caminho PostgreSQL
                """INSERT INTO clients (nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, senha_hash, patrimonio_investimento) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                params_pg
            )
            result = cur.fetchone()
            new_id = result[0] if result else None
        except Exception as e1:
            # Tenta SQLite com RETURNING (versão 3.35+)
            try:
                cur.execute(
                    """INSERT INTO clients (nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, senha_hash, patrimonio_investimento) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?) RETURNING id""",
                    params_sqlite
                )
                result = cur.fetchone()
                new_id = result[0] if result else None
            except Exception as e2:
                # Fallback: SQLite sem RETURNING
                cur.execute(
                    """INSERT INTO clients (nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, senha_hash, patrimonio_investimento) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    params_sqlite
                )
                cur.execute("SELECT MAX(id) FROM clients")
                result = cur.fetchone()
                new_id = result[0] if result and result[0] is not None else None
        
        conn.commit()
        
        if new_id is not None:
            return get_client(int(new_id))
        return None
    finally:
        if should_close:
            conn.close()


def update_client(client_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    import logging
    logger = logging.getLogger("storage")
    
    current = get_client(client_id)
    if not current:
        logger.error(f"update_client: Cliente {client_id} não encontrado")
        return None
    
    # Garantir que patrimonio_investimento existe
    if "patrimonio_investimento" not in current:
        current["patrimonio_investimento"] = 0.0
    
    # Hash da senha se fornecida
    if "senha" in data:
        _validate_password_strength(data["senha"])
        if _is_password_pwned(data["senha"]):
            raise ValueError("Senha comprometida em vazamentos. Escolha outra.")
        data["senha_hash"] = _hash_password(data.pop("senha"))

    # Aplicar delta SOMENTE se não vier patrimonio_investimento direto
    if data.get("patrimonio_investimento_delta") is not None and "patrimonio_investimento" not in data:
        delta = data.pop("patrimonio_investimento_delta")
        base = current.get("patrimonio_investimento") or 0.0
        data["patrimonio_investimento"] = base + delta
    elif "patrimonio_investimento_delta" in data:
        data.pop("patrimonio_investimento_delta")
    
    merged = {**current, **{k: v for k, v in data.items() if v is not None}}
    logger.info(f"update_client: {client_id} merged data: saldo_cc={merged.get('saldo_cc')}, patrimonio_investimento={merged.get('patrimonio_investimento')}")
    logger.info(f"update_client: {client_id} current patrimonio: {current.get('patrimonio_investimento')}, data patrimonio: {data.get('patrimonio_investimento')}")
    
    conn = get_connection()
    should_close = _should_close_connection(conn)
    try:
        cur = conn.cursor()
        _ensure_unique(conn, merged["email"], merged["telefone"], exclude_id=client_id)

        # Manter hash existente quando senha não for enviada
        try:
            cur.execute("SELECT senha_hash FROM clients WHERE id = ?", (client_id,))
        except Exception:
            cur.execute("SELECT senha_hash FROM clients WHERE id = %s", (client_id,))
        row_hash = cur.fetchone()
        current_hash = row_hash[0] if row_hash else None

        senha_hash_final = merged.get("senha_hash", current_hash)

        params = (
            merged["nome"],
            merged["telefone"],
            merged["email"],
            merged["data_nascimento"],
            merged["correntista"],
            merged["score_credito"],
            merged["saldo_cc"],
            merged["patrimonio_investimento"],
            senha_hash_final,
            client_id,
        )
        
        print(f"DEBUG update_client: params = {params}")
        print(f"DEBUG update_client: patrimonio_investimento em params[7] = {params[7]}")
        print(f"DEBUG merged patrimonio_investimento = {merged['patrimonio_investimento']}")
        print(f"DEBUG current patrimonio_investimento = {current.get('patrimonio_investimento')}")
        print(f"DEBUG data patrimonio_investimento = {data.get('patrimonio_investimento')}")
        
        try:
              print(f"DEBUG: Tentando UPDATE com SQLite placeholders (?)")
              cur.execute(  # pragma: no cover - caminho SQLite
                """UPDATE clients SET nome=?, telefone=?, email=?, data_nascimento=?, correntista=?, score_credito=?, saldo_cc=?, patrimonio_investimento=?, senha_hash=? 
                   WHERE id=?""",
                params
            )
              print(f"DEBUG: UPDATE com ? funcionou! Rows affected: {cur.rowcount}")
        except Exception as e1:
              print(f"DEBUG: SQLite falhou: {e1}")
              try:
                  print(f"DEBUG: Tentando UPDATE com PostgreSQL placeholders (%s)")
                  cur.execute(  # pragma: no cover - caminho PostgreSQL
                    """UPDATE clients SET nome=%s, telefone=%s, email=%s, data_nascimento=%s, correntista=%s, score_credito=%s, saldo_cc=%s, patrimonio_investimento=%s, senha_hash=%s 
                       WHERE id=%s""",
                    params
                )
                  print(f"DEBUG: UPDATE com %s funcionou! Rows affected: {cur.rowcount}")
                  if cur.rowcount == 0:
                      print(f"ERRO: UPDATE não afetou nenhuma linha! client_id={client_id}")
              except Exception as e2:
                  print(f"DEBUG: PostgreSQL falhou: {e2}")
                  logger.error(f"update_client: Falha ao executar UPDATE. SQLite: {e1}, PostgreSQL: {e2}")
                  raise e2
        
        # SQLite não tem autocommit, PostgreSQL sim
        try:
            if not conn.autocommit:
                conn.commit()
                logger.info(f"update_client: {client_id} commit manual realizado")
        except AttributeError:
            # SQLite: sempre fazer commit
            conn.commit()
            logger.info(f"update_client: {client_id} commit manual realizado (SQLite)")
        
        result = get_client(client_id)
        if result:
            print(f"DEBUG: Pós-UPDATE verificação - patrimonio_investimento={result.get('patrimonio_investimento')}")
            logger.info(f"update_client: {client_id} verificação pós-update saldo_cc={result.get('saldo_cc')}, patrimonio={result.get('patrimonio_investimento')}")
        return result
    finally:
        if should_close:
            conn.close()


def delete_client(client_id: int) -> bool:
    conn = get_connection()
    should_close = _should_close_connection(conn)
    try:
        cur = conn.cursor()
        
        try:
            cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        except Exception:
            cur.execute("DELETE FROM clients WHERE id = %s", (client_id,))
        
        conn.commit()
        return cur.rowcount > 0
    finally:
        if should_close:
            conn.close()


def login_client(email: str, senha: str) -> Optional[Dict[str, Any]]:
    """Autentica cliente por email e senha. Retorna cliente se sucesso, None se falha."""
    conn = get_connection()
    should_close = _should_close_connection(conn)
    try:
        cur = conn.cursor()
        _execute_query(
            conn,
            cur,
            "SELECT id, nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, senha_hash FROM clients WHERE email = ?",
            "SELECT id, nome, telefone, email, data_nascimento, correntista, score_credito, saldo_cc, senha_hash FROM clients WHERE email = %s",
            (email,)
        )
        row = cur.fetchone()
        if not row:
            return None
        
        # Verifica senha
        senha_hash = row[8]
        if not senha_hash or not _verify_password(senha, senha_hash):
            return None
        
        # Retorna cliente sem exposição de hash
        return _row_to_client(row[:8])
    finally:
        if should_close:
            conn.close()


def update_password(email: str, nova_senha: str) -> bool:
    """Atualiza a senha de um cliente usando hash bcrypt seguro.

    Parâmetros:
        email: Email do cliente
        nova_senha: Nova senha em texto plano (será hasheada)

    Retorno:
        True se a senha foi atualizada, False se o cliente não existe
    """
    conn = get_connection()
    should_close = _should_close_connection(conn)
    try:
        cur = conn.cursor()
        
        # Verifica se cliente existe
        _execute_query(
            conn,
            cur,
            "SELECT id FROM clients WHERE email = ?",
            "SELECT id FROM clients WHERE email = %s",
            (email,)
        )
        row = cur.fetchone()
        if not row:
            return False
        
        # Validação e hash da nova senha
        _validate_password_strength(nova_senha)
        if _is_password_pwned(nova_senha):
            raise ValueError("Senha comprometida em vazamentos. Escolha outra.")
        novo_hash = _hash_password(nova_senha)
        
        # Atualiza senha
        try:
              cur.execute(  # pragma: no cover - caminho PostgreSQL
                "UPDATE clients SET senha_hash = ? WHERE email = ?",
                (novo_hash, email)
            )
        except Exception:
              cur.execute(  # pragma: no cover - caminho PostgreSQL
                "UPDATE clients SET senha_hash = %s WHERE email = %s",
                (novo_hash, email)
            )
        
        conn.commit()
        return cur.rowcount > 0
    finally:
        if should_close:
            conn.close()
