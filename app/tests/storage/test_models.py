import pytest
from pydantic import ValidationError
from storage.models import ClientCreate, ClientUpdate


def test_client_create_valid():
    obj = ClientCreate(
        nome="Cliente",
        telefone=21999999999,
        correntista=True,
        score_credito=750.0,
        saldo_cc=12000.0
    )
    assert obj.nome == "Cliente"
    assert obj.correntista is True


def test_client_create_invalid_nome_vazio():
    with pytest.raises(ValidationError):
        ClientCreate(nome="", telefone=1, correntista=False)


def test_client_update_partial_and_types():
    u = ClientUpdate(saldo_cc=0.0, score_credito=0.0)
    assert u.saldo_cc == 0.0
    assert u.score_credito == 0.0
    u = ClientUpdate(telefone=0, correntista=False)
    assert u.telefone == 0
    assert u.correntista is False
