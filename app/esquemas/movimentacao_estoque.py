
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class MovimentacaoEstoqueCriacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    produto_id: int = Field(
        gt=0,
        description="Identificador do produto",
    )

    tipo: Literal["entrada", "saida"] = Field(
        description="Tipo da movimentação",
    )

    quantidade: int = Field(
        gt=0,
        description="Quantidade movimentada; deve ser maior que zero",
    )

    observacao: str | None = Field(
        default=None,
        max_length=255,
        description="Observação sobre a movimentação",
    )


class MovimentacaoEstoqueResposta(MovimentacaoEstoqueCriacao):
    id: int
    data_movimentacao: datetime

    model_config = ConfigDict(
        from_attributes=True,
        extra="forbid",
    )
