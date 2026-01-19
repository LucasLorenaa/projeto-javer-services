"""Comprehensive unit tests for gateway models with data_nascimento"""
import pytest
from datetime import date
from pydantic import ValidationError
from gateway.models import ClientCreate, ClientUpdate, ClientOut, ScoreOut


class TestClientCreate:
    """Test ClientCreate model validation"""
    
    def test_valid_minimal(self):
        """Test minimal valid ClientCreate"""
        c = ClientCreate(
            nome="João Silva",
            email="joao@example.com",
            telefone=21999999999,
            data_nascimento=date(1990, 5, 15),
            senha="SecurePass@123",
            correntista=False
        )
        assert c.nome == "João Silva"
        assert c.email == "joao@example.com"
        assert c.telefone == 21999999999
        assert c.data_nascimento == date(1990, 5, 15)
        assert c.senha == "SecurePass@123"
        assert c.correntista is False

    def test_valid_with_optional(self):
        """Test ClientCreate with optional fields"""
        c = ClientCreate(
            nome="Maria",
            email="maria@test.com",
            telefone=21988888888,
            data_nascimento=date(1995, 3, 20),
            senha="Pass@1234",
            correntista=True,
            score_credito=750.5,
            saldo_cc=5000.0
        )
        assert c.correntista is True
        assert c.score_credito == 750.5
        assert c.saldo_cc == 5000.0

    def test_invalid_nome_empty(self):
        """Test empty nome raises ValidationError"""
        with pytest.raises(ValidationError):
            ClientCreate(
                nome="",
                email="test@test.com",
                telefone=21999999999,
                data_nascimento=date(1990, 1, 1),
                senha="Pass@1234",
                correntista=False
            )

    def test_invalid_email(self):
        """Test invalid email raises ValidationError"""
        with pytest.raises(ValidationError):
            ClientCreate(
                nome="Test",
                email="not-an-email",
                telefone=21999999999,
                data_nascimento=date(1990, 1, 1),
                senha="Pass@1234",
                correntista=False
            )

    def test_invalid_telefone_type(self):
        """Test non-int telefone"""
        with pytest.raises(ValidationError):
            ClientCreate(
                nome="Test",
                email="test@test.com",
                telefone="not-a-number",
                data_nascimento=date(1990, 1, 1),
                senha="Pass@1234",
                correntista=False
            )

    def test_invalid_data_nascimento_type(self):
        """Test invalid data_nascimento type"""
        with pytest.raises(ValidationError):
            ClientCreate(
                nome="Test",
                email="test@test.com",
                telefone=21999999999,
                data_nascimento="not-a-date",
                senha="Pass@1234",
                correntista=False
            )

    def test_invalid_idade_minima(self):
        """Test age minimum validation (< 18 anos)"""
        with pytest.raises(ValidationError):
            ClientCreate(
                nome="Jovem",
                email="jovem@test.com",
                telefone=21999999999,
                data_nascimento=date(2010, 1, 1),  # 16 years old (too young)
                senha="Pass@1234",
                correntista=False
            )

    def test_valid_senha_length(self):
        """Test valid password lengths (6-20 chars)"""
        for pwd in ["123456", "My1Pass", "VeryLongPassword12"]:
            c = ClientCreate(
                nome="Test",
                email="test@test.com",
                telefone=21999999999,
                data_nascimento=date(1990, 1, 1),
                senha=pwd,
                correntista=False
            )
            assert c.senha == pwd

    def test_invalid_senha_too_short(self):
        """Test password too short (< 6)"""
        with pytest.raises(ValidationError):
            ClientCreate(
                nome="Test",
                email="test@test.com",
                telefone=21999999999,
                data_nascimento=date(1990, 1, 1),
                senha="short",
                correntista=False
            )

    def test_invalid_senha_too_long(self):
        """Test password too long (> 20)"""
        with pytest.raises(ValidationError):
            ClientCreate(
                nome="Test",
                email="test@test.com",
                telefone=21999999999,
                data_nascimento=date(1990, 1, 1),
                senha="thispasswordismuchlongerthantwetycharacteres",
                correntista=False
            )


class TestClientUpdate:
    """Test ClientUpdate model"""
    
    def test_all_fields_optional(self):
        """Test all fields are optional in ClientUpdate"""
        u = ClientUpdate()
        assert u.nome is None
        assert u.email is None
        assert u.telefone is None
        assert u.data_nascimento is None
        assert u.correntista is None
        assert u.score_credito is None
        assert u.saldo_cc is None

    def test_partial_update(self):
        """Test partial update with some fields"""
        u = ClientUpdate(
            email="newemail@test.com",
            telefone=21977777777
        )
        assert u.email == "newemail@test.com"
        assert u.telefone == 21977777777
        assert u.nome is None

    def test_financial_update(self):
        """Test updating financial fields"""
        u = ClientUpdate(
            score_credito=850.0,
            saldo_cc=25000.0
        )
        assert u.score_credito == 850.0
        assert u.saldo_cc == 25000.0

    def test_data_nascimento_update(self):
        """Test updating birth date"""
        new_date = date(1985, 6, 10)
        u = ClientUpdate(data_nascimento=new_date)
        assert u.data_nascimento == new_date


class TestClientOut:
    """Test ClientOut model (response)"""
    
    def test_client_out_complete(self):
        """Test complete ClientOut response"""
        out = ClientOut(
            id=1,
            nome="Test User",
            email="test@test.com",
            telefone=21999999999,
            data_nascimento=date(1990, 5, 15),
            correntista=True,
            score_credito=750.0,
            saldo_cc=5000.0
        )
        assert out.id == 1
        assert out.nome == "Test User"
        assert out.email == "test@test.com"
        assert out.data_nascimento == date(1990, 5, 15)
        assert out.correntista is True

    def test_client_out_from_dict(self):
        """Test ClientOut creation from dict"""
        data = {
            "id": 2,
            "nome": "Jane",
            "email": "jane@test.com",
            "telefone": 21988888888,
            "data_nascimento": date(1992, 3, 20),
            "correntista": False,
            "score_credito": None,
            "saldo_cc": None
        }
        out = ClientOut(**data)
        assert out.id == 2
        assert out.nome == "Jane"
        assert out.data_nascimento == date(1992, 3, 20)


class TestScoreOut:
    """Test ScoreOut model"""
    
    def test_score_out_complete(self):
        """Test complete ScoreOut"""
        s = ScoreOut(
            id=1,
            nome="John",
            saldo_cc=10000.0,
            score_calculado=1000.0
        )
        assert s.id == 1
        assert s.nome == "John"
        assert s.saldo_cc == 10000.0
        assert s.score_calculado == 1000.0

    def test_score_out_with_zero(self):
        """Test ScoreOut with zero values"""
        s = ScoreOut(id=1, nome="Zero", saldo_cc=0.0, score_calculado=0.0)
        assert s.saldo_cc == 0.0
        assert s.score_calculado == 0.0

    def test_score_out_from_dict(self):
        """Test ScoreOut from dict"""
        data = {"id": 5, "nome": "User5", "saldo_cc": 15000.0, "score_calculado": 1500.0}
        s = ScoreOut(**data)
        assert s.id == 5
        assert s.score_calculado == 1500.0
