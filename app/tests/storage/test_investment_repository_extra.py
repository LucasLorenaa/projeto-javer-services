import sqlite3
from unittest.mock import patch

import pytest

from storage import db
from storage.investment_repository import InvestmentRepository
from storage.models import InvestimentoCreate, InvestimentoUpdate, TipoInvestimento


@pytest.fixture(autouse=True)
def sqlite_conn(monkeypatch):
    if hasattr(db.get_connection, "_test_cache"):
        del db.get_connection._test_cache

    def _raise_operational_error(*args, **kwargs):
        raise db.psycopg2.OperationalError("fail")
    monkeypatch.setattr(db.psycopg2, "connect", _raise_operational_error)

    conn = db.get_connection()
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("DELETE FROM investments")
    conn.execute("DELETE FROM clients")
    conn.execute("INSERT INTO clients (id, nome, telefone, email, correntista) VALUES (1, 'Cli', 123, 'cli@test.com', 1)")
    conn.commit()
    yield conn
    conn.execute("DELETE FROM investments")
    conn.execute("DELETE FROM clients")
    conn.commit()
    if hasattr(db.get_connection, "_test_cache"):
        del db.get_connection._test_cache


def test_create_and_get_investments(sqlite_conn):
    inv = InvestimentoCreate(
        cliente_id=1,
        tipo_investimento=TipoInvestimento.ACOES,
        ticker="AAPL",
        valor_investido=100.0,
        rentabilidade=1.5,
        ativo=True,
    )
    created = InvestmentRepository.create(inv)
    assert created.id is not None

    all_items = InvestmentRepository.get_all()
    assert any(item.id == created.id for item in all_items)

    by_id = InvestmentRepository.get_by_id(created.id)
    assert by_id is not None

    by_cliente = InvestmentRepository.get_by_cliente(1)
    assert len(by_cliente) >= 1


def test_update_investment(sqlite_conn):
    inv = InvestimentoCreate(
        cliente_id=1,
        tipo_investimento=TipoInvestimento.ACOES,
        ticker="AAPL",
        valor_investido=50.0,
        rentabilidade=0.0,
        ativo=True,
    )
    created = InvestmentRepository.create(inv)

    updated = InvestmentRepository.update(created.id, InvestimentoUpdate(valor_investido=75.0, ativo=False))
    assert updated.valor_investido == 75.0
    assert updated.ativo is False

    # Update with no fields returns existing unchanged
    same = InvestmentRepository.update(created.id, InvestimentoUpdate())
    assert same.id == created.id


def test_delete_and_total(sqlite_conn):
    inv1 = InvestimentoCreate(
        cliente_id=1,
        tipo_investimento=TipoInvestimento.ACOES,
        ticker="AAPL",
        valor_investido=100.0,
        ativo=True,
    )
    inv2 = InvestimentoCreate(
        cliente_id=1,
        tipo_investimento=TipoInvestimento.ACOES,
        ticker="MSFT",
        valor_investido=300.0,
        ativo=False,
    )
    created1 = InvestmentRepository.create(inv1)
    InvestmentRepository.create(inv2)

    total = InvestmentRepository.get_total_investido_cliente(1)
    assert total == 100.0

    assert InvestmentRepository.delete(created1.id) is True
    assert InvestmentRepository.delete(9999) is False
