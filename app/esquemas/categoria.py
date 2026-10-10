from pydantic import BaseModel, ConfigDict, Field


class CategoriaBase(BaseModel):
    nome: str = Field(
        min_length=1,
        max_length=100,
        description="Nome da categoria",
    )

    descricao: str | None = Field(
        default=None,
        max_length=255,
        description="Descrição da categoria",
    )


class CategoriaCriacao(CategoriaBase):
    pass


class CategoriaResposta(CategoriaBase):
    id: int

    model_config = ConfigDict(from_attributes=True)