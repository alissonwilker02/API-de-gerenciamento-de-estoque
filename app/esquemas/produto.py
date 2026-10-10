from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(
        min_length=1,
        max_length=150,
        description="Nome do produto",
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
        description="Descrição do produto",
    )

    preco: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Preço unitário do produto,"
    )

    quantidade_estoque: int = Field(
        default=0,
        ge=0,
        description="Quantidade atual em estoque",
    )

    estoque_minimo: int = Field(
        default=5,
        ge=0,
        description="Quantidade minima desejada em estoque",
    )

    categoria_id: int = Field(
        gt=0,
        description="Identificador da categoria",
    )

    fornecedor_id: int = Field(
        gt=0,
        description="Identificador do fornecedor",
    )


class ProdutoCriacao(ProdutoBase):
    pass


class ProdutoResposta(ProdutoBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
