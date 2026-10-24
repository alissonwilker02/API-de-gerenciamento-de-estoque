
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: str = Field(
        min_length=1,
        max_length=150,
        description="Nome do produto",
    )

    sku: str = Field(
        min_length=1,
        max_length=50,
        description="Código único de identificação do produto",
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
        description="Descrição do produto",
    )

    preco_custo: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Preço de custo do produto",
    )

    preco_venda: Decimal = Field(
        gt=0,
        max_digits=10,
        decimal_places=2,
        description="Preço de venda do produto",
    )

    estoque_minimo: int = Field(
        default=5,
        ge=0,
        description="Quantidade mínima desejada em estoque",
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
    # O estoque inicial é zero.
    # Entradas e saídas são registradas por movimentações.
    pass


class ProdutoAtualizacao(ProdutoBase):
    pass


class ProdutoResposta(ProdutoBase):
    id: int
    quantidade_estoque: int
    data_cadastro: datetime

    model_config = ConfigDict(from_attributes=True)
