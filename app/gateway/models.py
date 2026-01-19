from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import date

class ClientBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    telefone: Optional[int] = Field(default=None, ge=0)
    email: EmailStr
    data_nascimento: date
    correntista: Optional[bool] = None
    score_credito: Optional[float] = Field(default=None, ge=0)
    saldo_cc: Optional[float] = Field(default=None, ge=0)

    @validator("data_nascimento")
    def validar_idade_minima(cls, v):  # noqa: D417
        from datetime import datetime
        if v is None:
            return v
        hoje = datetime.now().date()
        idade = hoje.year - v.year - ((hoje.month, hoje.day) < (v.month, v.day))
        if idade < 18:
            raise ValueError("Deve ter no mínimo 18 anos")
        return v

class ClientCreate(ClientBase):
    senha: str = Field(..., min_length=6, max_length=20)

class ClientRegister(BaseModel):
    """Modelo para registro de novo cliente via login."""
    email: EmailStr
    senha: str = Field(..., min_length=6, max_length=20)
    nome: str = Field(..., min_length=1, max_length=255)
    telefone: Optional[int] = Field(default=None, ge=0)
    data_nascimento: date
    correntista: Optional[bool] = Field(default=False)

    @validator("data_nascimento")
    def validar_idade_minima(cls, v):  # noqa: D417
        from datetime import datetime
        if v is None:
            return v
        hoje = datetime.now().date()
        idade = hoje.year - v.year - ((hoje.month, hoje.day) < (v.month, v.day))
        if idade < 18:
            raise ValueError("Deve ter no mínimo 18 anos")
        return v

class ClientLogin(BaseModel):
    """Modelo para login de cliente."""
    email: EmailStr
    senha: str

class ClientPasswordReset(BaseModel):
    """Modelo para resetar senha de cliente."""
    email: EmailStr
    senha_atual: Optional[str] = None
    senha_nova: str = Field(..., min_length=6, max_length=20)

class ClientUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=255)
    telefone: Optional[int] = Field(default=None, ge=0)
    email: Optional[EmailStr] = None
    data_nascimento: Optional[date] = None
    correntista: Optional[bool] = None
    score_credito: Optional[float] = Field(default=None, ge=0)
    saldo_cc: Optional[float] = Field(default=None, ge=0)

    @validator("data_nascimento")
    def validar_idade_minima(cls, v):  # noqa: D417
        from datetime import datetime
        if v is None:
            return v
        hoje = datetime.now().date()
        idade = hoje.year - v.year - ((hoje.month, hoje.day) < (v.month, v.day))
        if idade < 18:
            raise ValueError("Deve ter no mínimo 18 anos")
        return v

class ClientOut(ClientBase):
    id: int
    email: Optional[EmailStr] = None
    data_nascimento: Optional[date] = None


class ScoreOut(BaseModel):
    id: int
    nome: str
    saldo_cc: Optional[float]
    score_calculado: Optional[float]
