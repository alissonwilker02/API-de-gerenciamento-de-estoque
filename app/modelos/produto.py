
from sqlalchemy import Column, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import relationship

from app.banco_de_dados import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150), nullable=False)
    descricao = Column(String(255), nullable=True)
    preco = Column(Numeric(10, 2), nullable=False)
    quantidade_estoque = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=5)

    categoria_id = Column(
        Integer,
        ForeignKey("categorias.id"),
        nullable=False,
    )

    fornecedor_id = Column(
        Integer,
        ForeignKey("fornecedores.id"),
        nullable=False,
    )

    categoria = relationship("Categoria")
    fornecedor = relationship("Fornecedor")
