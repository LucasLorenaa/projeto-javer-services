from datetime import date, timedelta
import pytest

from gateway import models


def test_client_base_underage_raises():
    underage = date.today() - timedelta(days=17 * 365)
    with pytest.raises(ValueError):
        models.ClientBase(
            nome="Ana",
            telefone=123,
            email="ana@test.com",
            data_nascimento=underage,
            saldo_cc=0,
        )


def test_client_register_underage_raises():
    underage = date.today() - timedelta(days=17 * 365)
    with pytest.raises(ValueError):
        models.ClientRegister(
            email="ana@test.com",
            senha="segura123",
            nome="Ana",
            telefone=123,
            data_nascimento=underage,
        )


def test_client_update_underage_raises():
    underage = date.today() - timedelta(days=17 * 365)
    with pytest.raises(ValueError):
        models.ClientUpdate(data_nascimento=underage)
