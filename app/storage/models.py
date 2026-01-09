from typing import Optional
from pydantic import BaseModel, Field

class ClientBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    # telefone como inteiro; aceita valores não-negativos para testes/dev
    telefone: int = Field(..., ge=0)
    correntista: bool
    score_credito: Optional[float] = Field(default=None, ge=0)
    saldo_cc: Optional[float] = Field(default=None, ge=0)

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=1, max_length=255)
    telefone: Optional[int] = Field(default=None, ge=0)
    correntista: Optional[bool] = None
    score_credito: Optional[float] = Field(default=None, ge=0)
    saldo_cc: Optional[float] = Field(default=None, ge=0)

class ClientOut(ClientBase):
    id: int
