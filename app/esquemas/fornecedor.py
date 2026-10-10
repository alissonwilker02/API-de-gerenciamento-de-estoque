
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class FornecedorBase(BaseModel):
    nome: str = Field(
        min_length=1,
        max_length=150,
        description="Nome do fornecedor",
    )

    email: EmailStr | None = Field(
        default=None,
        description="E-mail do fornecedor",
    )

    telefone: str | None = Field(
        default=None,
        max_length=20,
        description="Telefone do fornecedor",
    )


class FornecedorCriacao(FornecedorBase):
    pass


class FornecedorResposta(FornecedorBase):
    id: int

    model_config = ConfigDict(from_attributes=True)