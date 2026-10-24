
import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class FornecedorBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(
        min_length=1,
        max_length=150,
        description="Nome do fornecedor",
    )

    cnpj: str = Field(
        min_length=14,
        max_length=18,
        description="CNPJ do fornecedor",
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

    @field_validator("cnpj")
    @classmethod
    def validar_cnpj(cls, valor: str) -> str:
        # Aceita CNPJ com ou sem pontuação, armazenando apenas os dígitos.
        cnpj = re.sub(r"\D", "", valor)

        if len(cnpj) != 14:
            raise ValueError("O CNPJ deve conter exatamente 14 dígitos.")

        if len(set(cnpj)) == 1:
            raise ValueError("O CNPJ informado é inválido.")

        return cnpj


class FornecedorCriacao(FornecedorBase):
    pass


class FornecedorAtualizacao(FornecedorBase):
    pass


class FornecedorResposta(FornecedorBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )
