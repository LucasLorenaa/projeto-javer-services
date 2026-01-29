from typing import Optional
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import date, datetime
from enum import Enum

class ClientBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=255)
    telefone: Optional[int] = Field(default=None, ge=0)
    email: EmailStr
    data_nascimento: date
    correntista: Optional[bool] = None
    score_credito: Optional[float] = Field(default=None, ge=0)
    saldo_cc: Optional[float] = Field(default=None, ge=0)
    patrimonio_investimento: Optional[float] = Field(default=0.0, ge=0)

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
    patrimonio_investimento: Optional[float] = Field(default=None, ge=0)
    patrimonio_investimento_delta: Optional[float] = Field(default=None, ge=0)

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


# ============ MODELOS DE INVESTIMENTO ============

class PerfilInvestidor(str, Enum):
    """Perfil de risco do investidor."""
    CONSERVADOR = "CONSERVADOR"
    MODERADO = "MODERADO"
    ARROJADO = "ARROJADO"


class TipoInvestimento(str, Enum):
    """Tipos de investimento disponíveis."""
    RENDA_FIXA = "RENDA_FIXA"
    ACOES = "ACOES"
    FUNDOS = "FUNDOS"
    CRIPTO = "CRIPTO"


class InvestimentoBase(BaseModel):
    """Modelo base para investimento."""
    cliente_id: int
    tipo_investimento: TipoInvestimento
    ticker: Optional[str] = Field(default=None, description="Código do ativo (ex: PETR4.SA, BTC-USD)")
    valor_investido: float = Field(..., gt=0, description="Valor investido em reais")
    rentabilidade: Optional[float] = Field(default=0.0, description="Rentabilidade acumulada (%)")
    ativo: bool = Field(default=True, description="Se o investimento está ativo")


class InvestimentoCreate(InvestimentoBase):
    """Modelo para criar investimento."""
    pass


class InvestimentoUpdate(BaseModel):
    """Modelo para atualizar investimento."""
    tipo_investimento: Optional[TipoInvestimento] = None
    ticker: Optional[str] = None
    valor_investido: Optional[float] = Field(default=None, gt=0)
    rentabilidade: Optional[float] = None
    ativo: Optional[bool] = None


class InvestimentoOut(InvestimentoBase):
    """Modelo de saída para investimento."""
    id: int
    data_aplicacao: datetime

    class Config:
        from_attributes = True


# ============ MODELOS DE ANÁLISE ============

class ProjecaoRetorno(BaseModel):
    """Modelo para projeção de retorno anual."""
    cliente_id: int
    nome: str
    perfil_investidor: PerfilInvestidor
    patrimonio_total: float
    projecao_anual: float
    taxa_retorno: float


class PatrimonioCliente(BaseModel):
    """Modelo para cálculo de patrimônio."""
    cliente_id: int
    nome: str
    saldo_conta: float
    total_investimentos: float
    patrimonio_total: float


class AnaliseMercado(BaseModel):
    """Modelo para análise de mercado de um ticker."""
    ticker: str
    preco_atual: Optional[float]
    variacao_dia: Optional[float]
    variacao_percentual: Optional[float]
    volume: Optional[int]
    historico_disponivel: bool
