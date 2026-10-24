from pydantic import BaseModel


class ErroDetalhe(BaseModel):
    codigo: int
    mensagem: str


class ErroResposta(BaseModel):
    erro: ErroDetalhe
