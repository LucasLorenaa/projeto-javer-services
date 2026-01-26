import datetime
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch

from storage.main import app
from storage.repository import create_client
from storage.investment_repository import InvestmentRepository
from storage.models import InvestimentoCreate, TipoInvestimento

client = TestClient(app)


def _seed_client():
    unique = int(datetime.datetime.now().timestamp() * 1000)
    data = {
        "nome": "Alice",
        "telefone": unique,
        "email": f"alice{unique}@example.com",
        "data_nascimento": datetime.date(1990, 1, 1),
        "correntista": True,
        "score_credito": 100.0,
        "saldo_cc": 500.0,
    }
    with patch("storage.repository._is_password_pwned", return_value=False):
        created = create_client({**data, "senha": "senhaBoa123"})
    return created


def test_storage_models_underage_validator():
    from storage.models import ClientCreate, ClientRegister, ClientUpdate

    minor_birth = datetime.date.today().replace(year=datetime.date.today().year - 10)
    with pytest.raises(Exception):
        ClientCreate(
            nome="Menor",
            telefone=111,
            email="m1@test.com",
            data_nascimento=minor_birth,
            correntista=True,
            senha="senhaBoa123",
        )
    with pytest.raises(Exception):
        ClientRegister(
            email="m2@test.com",
            senha="senhaBoa123",
            nome="Menor",
            telefone=111,
            data_nascimento=minor_birth,
        )
    with pytest.raises(Exception):
        ClientUpdate(data_nascimento=minor_birth)


def test_password_min_length_raises():
    from storage.main import api_update_password
    class Dummy:
        email = "x@example.com"
        senha_nova = "123"
    with pytest.raises(Exception):
        api_update_password(Dummy())


def test_password_client_not_found():
    payload = {"email": "nobody@example.com", "senha_nova": "segura123"}
    resp = client.put("/password", json=payload)
    assert resp.status_code == 404


def test_get_investment_success_and_list_by_cliente():
    c = _seed_client()
    inv = InvestmentRepository.create(
        InvestimentoCreate(
            cliente_id=c["id"],
            tipo_investimento=TipoInvestimento.RENDA_FIXA,
            valor_investido=100.0,
            rentabilidade=0.0,
            ativo=True,
            ticker=None,
        )
    )
    # Buscar por ID
    resp = client.get(f"/investments/{inv.id}")
    assert resp.status_code == 200
    # Listar por cliente
    resp_list = client.get(f"/investments/cliente/{c['id']}")
    assert resp_list.status_code == 200
    assert any(item["id"] == inv.id for item in resp_list.json())


@patch("storage.investment_repository.InvestmentRepository.update", side_effect=ValueError("bad"))
def test_update_investment_value_error(mock_update):
    payload = {"valor_investido": 200.0}
    resp = client.put("/investments/123", json=payload)
    assert resp.status_code == 400


def test_delete_investment_success():
    c = _seed_client()
    inv = InvestmentRepository.create(
        InvestimentoCreate(
            cliente_id=c["id"],
            tipo_investimento=TipoInvestimento.ACOES,
            valor_investido=50.0,
            rentabilidade=0.0,
            ativo=True,
            ticker=None,
        )
    )
    resp = client.delete(f"/investments/{inv.id}")
    assert resp.status_code == 204
