"""Repositório para gerenciar investimentos no banco de dados."""
from typing import List, Optional
from datetime import datetime
from .db import get_connection
from .models import InvestimentoCreate, InvestimentoUpdate, InvestimentoOut, TipoInvestimento


class InvestmentRepository:
    """Repositório para operações CRUD de investimentos."""

    @staticmethod
    def create(investimento: InvestimentoCreate) -> InvestimentoOut:
        """Cria um novo investimento."""
        conn = get_connection()
        cur = conn.cursor()
        
        import sqlite3
        if isinstance(conn, sqlite3.Connection):
            cur.execute(
                """
                INSERT INTO investments (cliente_id, tipo_investimento, ticker, valor_investido, rentabilidade, ativo)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    investimento.cliente_id,
                    investimento.tipo_investimento.value,
                    investimento.ticker,
                    investimento.valor_investido,
                    investimento.rentabilidade or 0.0,
                    1 if investimento.ativo else 0,
                ),
            )
            inv_id = cur.lastrowid
            conn.commit()
        else:  # pragma: no cover - caminho usado apenas com PostgreSQL em produção
            cur.execute(
                """
                INSERT INTO investments (cliente_id, tipo_investimento, ticker, valor_investido, rentabilidade, ativo)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, data_aplicacao
                """,
                (
                    investimento.cliente_id,
                    investimento.tipo_investimento.value,
                    investimento.ticker,
                    investimento.valor_investido,
                    investimento.rentabilidade or 0.0,
                    investimento.ativo,
                ),
            )
            result = cur.fetchone()
            inv_id, data_aplicacao = result
            conn.commit()

        return InvestmentRepository.get_by_id(inv_id)

    @staticmethod
    def get_all() -> List[InvestimentoOut]:
        """Retorna todos os investimentos."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, cliente_id, tipo_investimento, ticker, valor_investido, 
                   rentabilidade, ativo, data_aplicacao
            FROM investments
            ORDER BY data_aplicacao DESC
            """
        )
        rows = cur.fetchall()
        
        return [
            InvestimentoOut(
                id=row[0],
                cliente_id=row[1],
                tipo_investimento=TipoInvestimento(row[2]),
                ticker=row[3],
                valor_investido=row[4],
                rentabilidade=row[5],
                ativo=bool(row[6]),
                data_aplicacao=row[7] if isinstance(row[7], datetime) else datetime.fromisoformat(str(row[7])),
            )
            for row in rows
        ]

    @staticmethod
    def get_by_id(investimento_id: int) -> Optional[InvestimentoOut]:
        """Retorna um investimento pelo ID."""
        conn = get_connection()
        cur = conn.cursor()
        import sqlite3
        if isinstance(conn, sqlite3.Connection):
            cur.execute(
                """
                SELECT id, cliente_id, tipo_investimento, ticker, valor_investido,
                       rentabilidade, ativo, data_aplicacao
                FROM investments
                WHERE id = ?
                """,
                (investimento_id,),
            )
        else:  # pragma: no cover - caminho PostgreSQL
            cur.execute(
                """
                SELECT id, cliente_id, tipo_investimento, ticker, valor_investido,
                       rentabilidade, ativo, data_aplicacao
                FROM investments
                WHERE id = %s
                """,
                (investimento_id,),
            )
        row = cur.fetchone()
        
        if not row:
            return None
        
        return InvestimentoOut(
            id=row[0],
            cliente_id=row[1],
            tipo_investimento=TipoInvestimento(row[2]),
            ticker=row[3],
            valor_investido=row[4],
            rentabilidade=row[5],
            ativo=bool(row[6]),
            data_aplicacao=row[7] if isinstance(row[7], datetime) else datetime.fromisoformat(str(row[7])),
        )

    @staticmethod
    def get_by_cliente(cliente_id: int) -> List[InvestimentoOut]:
        """Retorna todos os investimentos de um cliente."""
        conn = get_connection()
        cur = conn.cursor()
        import sqlite3
        if isinstance(conn, sqlite3.Connection):
            cur.execute(
                """
                SELECT id, cliente_id, tipo_investimento, ticker, valor_investido,
                       rentabilidade, ativo, data_aplicacao
                FROM investments
                WHERE cliente_id = ?
                ORDER BY data_aplicacao DESC
                """,
                (cliente_id,),
            )
        else:  # pragma: no cover - caminho PostgreSQL
            cur.execute(
                """
                SELECT id, cliente_id, tipo_investimento, ticker, valor_investido,
                       rentabilidade, ativo, data_aplicacao
                FROM investments
                WHERE cliente_id = %s
                ORDER BY data_aplicacao DESC
                """,
                (cliente_id,),
            )
        rows = cur.fetchall()
        
        return [
            InvestimentoOut(
                id=row[0],
                cliente_id=row[1],
                tipo_investimento=TipoInvestimento(row[2]),
                ticker=row[3],
                valor_investido=row[4],
                rentabilidade=row[5],
                ativo=bool(row[6]),
                data_aplicacao=row[7] if isinstance(row[7], datetime) else datetime.fromisoformat(str(row[7])),
            )
            for row in rows
        ]

    @staticmethod
    def update(investimento_id: int, data: InvestimentoUpdate) -> Optional[InvestimentoOut]:
        """Atualiza um investimento."""
        conn = get_connection()
        cur = conn.cursor()
        import sqlite3
        
        # Construir query dinâmica apenas com campos fornecidos
        updates = []
        valores = []
        placeholder = "%s" if not isinstance(conn, sqlite3.Connection) else "?"
        
        if data.tipo_investimento is not None:
            updates.append(f"tipo_investimento = {placeholder}")
            valores.append(data.tipo_investimento.value)
        
        if data.ticker is not None:
            updates.append(f"ticker = {placeholder}")
            valores.append(data.ticker)
        
        if data.valor_investido is not None:
            updates.append(f"valor_investido = {placeholder}")
            valores.append(data.valor_investido)
        
        if data.rentabilidade is not None:
            updates.append(f"rentabilidade = {placeholder}")
            valores.append(data.rentabilidade)
        
        if data.ativo is not None:
            updates.append(f"ativo = {placeholder}")
            valores.append(data.ativo)
        
        if not updates:
            return InvestmentRepository.get_by_id(investimento_id)
        
        valores.append(investimento_id)
        
        if isinstance(conn, sqlite3.Connection):
            query = f"UPDATE investments SET {', '.join(updates)} WHERE id = ?"
        else:  # pragma: no cover - caminho PostgreSQL
            query = f"UPDATE investments SET {', '.join(updates)} WHERE id = %s"
        cur.execute(query, tuple(valores))
        conn.commit()
        
        return InvestmentRepository.get_by_id(investimento_id)

    @staticmethod
    def delete(investimento_id: int) -> bool:
        """Deleta um investimento."""
        conn = get_connection()
        cur = conn.cursor()
        import sqlite3
        if isinstance(conn, sqlite3.Connection):
            cur.execute("DELETE FROM investments WHERE id = ?", (investimento_id,))
        else:  # pragma: no cover - caminho PostgreSQL
            cur.execute("DELETE FROM investments WHERE id = %s", (investimento_id,))
        conn.commit()
        
        return cur.rowcount > 0

    @staticmethod
    def get_total_investido_cliente(cliente_id: int) -> float:
        """Retorna o total investido por um cliente (apenas investimentos ativos)."""
        conn = get_connection()
        cur = conn.cursor()
        import sqlite3
        if isinstance(conn, sqlite3.Connection):
            cur.execute(
                """
                SELECT COALESCE(SUM(valor_investido), 0)
                FROM investments
                WHERE cliente_id = ? AND ativo = 1
                """,
                (cliente_id,),
            )
        else:  # pragma: no cover - caminho PostgreSQL
            cur.execute(
                """
                SELECT COALESCE(SUM(valor_investido), 0)
                FROM investments
                WHERE cliente_id = %s AND ativo = TRUE
                """,
                (cliente_id,),
            )
        result = cur.fetchone()
        
        return float(result[0]) if result else 0.0
