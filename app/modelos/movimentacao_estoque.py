
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.banco_de_dados import Base


class MovimentacaoEstoque(Base):
    __tablename__ = "movimentacoes_estoque"

    id = Column(Integer, primary_key=True, index=True)

    produto_id = Column(
        Integer,
        ForeignKey("produtos.id"),
        nullable=False,
    )

    tipo = Column(String(10), nullable=False)
    quantidade = Column(Integer, nullable=False)
    observacao = Column(String(255), nullable=True)

    data_movimentacao = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    produto = relationship("Produto")
