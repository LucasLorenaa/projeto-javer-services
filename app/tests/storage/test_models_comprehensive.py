"""Comprehensive unit tests for storage models"""
import pytest
from datetime import date
from pydantic import ValidationError
from storage.models import ClientBase, ClientRegister, ClientUpdate, ClientOut


class TestClientBase:
    """Test ClientBase model"""
    
    def test_client_base_valid(self):
        """Test valid ClientBase"""
        c = ClientBase(
            nome="João Silva",
            telefone=21999999999,
            email="joao@test.com",
            data_nascimento=date(1990, 5, 15),
            correntista=False
        )
        assert c.nome == "João Silva"
        assert c.telefone == 21999999999
        assert c.email == "joao@test.com"
        assert c.data_nascimento == date(1990, 5, 15)
        assert c.correntista is False

    def test_client_base_invalid_email(self):
        """Test invalid email format"""
        with pytest.raises(ValidationError):
            ClientBase(
                nome="Test",
                telefone=21999999999,
                email="not-an-email",
                data_nascimento=date(1990, 1, 1),
                correntista=False
            )

    def test_client_base_invalid_telefone(self):
        """Test invalid telefone type"""
        with pytest.raises(ValidationError):
            ClientBase(
                nome="Test",
                telefone="not-a-number",
                email="test@test.com",
                data_nascimento=date(1990, 1, 1),
                correntista=False
            )


class TestClientRegister:
    """Test ClientRegister model"""
    
    def test_client_register_minimal(self):
        """Test minimal ClientRegister"""
        c = ClientRegister(
            nome="Maria",
            telefone=21988888888,
            email="maria@test.com",
            data_nascimento=date(1995, 3, 20),
            senha="SecurePass@123"
        )
        assert c.senha == "SecurePass@123"
        assert c.correntista is False

    def test_client_register_with_correntista(self):
        """Test ClientRegister with correntista=True"""
        c = ClientRegister(
            nome="Pedro",
            telefone=21977777777,
            email="pedro@test.com",
            data_nascimento=date(1992, 6, 10),
            senha="Password@123",
            correntista=True
        )
        assert c.correntista is True

    def test_client_register_missing_senha(self):
        """Test ClientRegister without senha"""
        with pytest.raises(ValidationError):
            ClientRegister(
                nome="Test",
                telefone=21999999999,
                email="test@test.com",
                data_nascimento=date(1990, 1, 1)
            )


class TestClientUpdate:
    """Test ClientUpdate model"""
    
    def test_client_update_all_optional(self):
        """Test all fields are optional"""
        u = ClientUpdate()
        assert u.nome is None
        assert u.telefone is None
        assert u.email is None
        assert u.data_nascimento is None
        assert u.correntista is None
        assert u.score_credito is None
        assert u.saldo_cc is None

    def test_client_update_partial(self):
        """Test partial update"""
        u = ClientUpdate(
            email="newemail@test.com",
            telefone=21966666666
        )
        assert u.email == "newemail@test.com"
        assert u.telefone == 21966666666
        assert u.nome is None

    def test_client_update_financial(self):
        """Test updating financial fields"""
        u = ClientUpdate(
            score_credito=850.0,
            saldo_cc=25000.0,
            correntista=True
        )
        assert u.score_credito == 850.0
        assert u.saldo_cc == 25000.0
        assert u.correntista is True

    def test_client_update_data_nascimento(self):
        """Test updating birth date"""
        new_date = date(1985, 12, 25)
        u = ClientUpdate(data_nascimento=new_date)
        assert u.data_nascimento == new_date


class TestClientOut:
    """Test ClientOut model"""
    
    def test_client_out_complete(self):
        """Test complete ClientOut"""
        c = ClientOut(
            id=1,
            nome="Test User",
            telefone=21999999999,
            email="test@test.com",
            data_nascimento=date(1990, 5, 15),
            correntista=False,
            score_credito=None,
            saldo_cc=None
        )
        assert c.id == 1
        assert c.nome == "Test User"
        assert c.data_nascimento == date(1990, 5, 15)
        assert c.correntista is False

    def test_client_out_with_financial(self):
        """Test ClientOut with financial data"""
        c = ClientOut(
            id=2,
            nome="Rich User",
            telefone=21988888888,
            email="rich@test.com",
            data_nascimento=date(1980, 1, 1),
            correntista=True,
            score_credito=900.0,
            saldo_cc=50000.0
        )
        assert c.correntista is True
        assert c.score_credito == 900.0
        assert c.saldo_cc == 50000.0

    def test_client_out_from_dict(self):
        """Test ClientOut from dict"""
        data = {
            "id": 3,
            "nome": "Dict User",
            "telefone": 21977777777,
            "email": "dict@test.com",
            "data_nascimento": date(1995, 6, 20),
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        c = ClientOut(**data)
        assert c.id == 3
        assert c.data_nascimento == date(1995, 6, 20)
        assert c.correntista is False

