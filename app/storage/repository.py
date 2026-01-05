from typing import List, Optional, Dict, Any
from .db import get_connection


def _row_to_client(row) -> Dict[str, Any]:
    return {
        "id": row[0],
        "nome": row[1],
        "telefone": int(row[2]),
        "correntista": bool(row[3]),
        "score_credito": float(row[4]) if row[4] is not None else None,
        "saldo_cc": float(row[5]) if row[5] is not None else None,
    }


def list_clients() -> List[Dict[str, Any]]:
    conn = get_connection()
    # avoid closing cached sqlite connections (they are reused across tests)
    should_close = True
    if hasattr(get_connection, "_sqlite_cache") and conn in get_connection._sqlite_cache.values():
        should_close = False
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nome, telefone, correntista, score_credito, saldo_cc FROM clients")
        rows = cur.fetchall()
        return [_row_to_client(r) for r in rows]
    finally:
        if should_close:
            conn.close()


def get_client(client_id: int) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    should_close = True
    if hasattr(get_connection, "_sqlite_cache") and conn in get_connection._sqlite_cache.values():
        should_close = False
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, nome, telefone, correntista, score_credito, saldo_cc FROM clients WHERE id = ?", (client_id,))
        row = cur.fetchone()
        return _row_to_client(row) if row else None
    finally:
        if should_close:
            conn.close()



def create_client(data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    conn = get_connection()
    should_close = True
    if hasattr(get_connection, "_sqlite_cache") and conn in get_connection._sqlite_cache.values():
        should_close = False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO clients (nome, telefone, correntista, score_credito, saldo_cc) VALUES (?, ?, ?, ?, ?)",
            (data["nome"], data["telefone"], data["correntista"], data.get("score_credito"), data.get("saldo_cc"))
        )
        # Commit the insert, then get the generated id in a DB-agnostic way
        conn.commit()
        cur.execute("SELECT MAX(id) FROM clients")
        row = cur.fetchone()
        new_id = row[0] if row and row[0] is not None else None

        if new_id is not None:
            return get_client(int(new_id))
        return None
    finally:
        if should_close:
            conn.close()

def update_client(client_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    current = get_client(client_id)
    if not current:
        return None
    merged = {**current, **{k: v for k, v in data.items() if v is not None}}
    conn = get_connection()
    should_close = True
    if hasattr(get_connection, "_sqlite_cache") and conn in get_connection._sqlite_cache.values():
        should_close = False
    try:
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE clients SET nome=?, telefone=?, correntista=?, score_credito=?, saldo_cc=? WHERE id=?
            """,
            (merged["nome"], merged["telefone"], merged["correntista"], merged["score_credito"], merged["saldo_cc"], client_id)
        )
        conn.commit()
        return get_client(client_id)
    finally:
        if should_close:
            conn.close()


def delete_client(client_id: int) -> bool:
    conn = get_connection()
    should_close = True
    if hasattr(get_connection, "_sqlite_cache") and conn in get_connection._sqlite_cache.values():
        should_close = False
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        if should_close:
            conn.close()
