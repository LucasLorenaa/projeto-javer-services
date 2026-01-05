
# tests/gateway/unit/test_models.py
import pytest
from pydantic import ValidationError
from gateway.models import ClientCreate, ClientUpdate, ClientOut, ScoreOut


def test_client_create_valido():
    c = ClientCreate(
        nome="Cliente Gateway",
        telefone=21999999999,
        correntista=True,
        score_credito=780.5,
        saldo_cc=15000.0,
    )
    assert c.nome == "Cliente Gateway"
    assert c.correntista is True
    assert isinstance(c.telefone, int)
    assert isinstance(c.saldo_cc, float)


def test_client_create_nome_invalido():
    with pytest.raises(ValidationError):
        ClientCreate(nome="", telefone=1, correntista=False)


def test_client_update_parcial():
    u = ClientUpdate(saldo_cc=0.0, score_credito=0.0)
    assert u.saldo_cc == 0.0
    assert u.score_credito == 0.0

    u2 = ClientUpdate(telefone=0, correntista=False)
    assert u2.telefone == 0
    assert u2.correntista is False


def test_client_out_estrutura():
    base = ClientCreate(nome="X", telefone=55, correntista=False)
    out = ClientOut(id=1, **base.model_dump())
    assert out.id == 1
    assert out.nome == "X"
    assert out.correntista is False


def test_score_out_estrutura():
    s = ScoreOut(id=1, nome="X", saldo_cc=200.0, score_calculado=20.0)
    assert s.id == 1
    assert s.nome == "X"
    assert s.saldo_cc == 200.0
    assert s.score_calculado == 20.0
