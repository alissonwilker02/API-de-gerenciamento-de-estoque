
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship

from app.banco_de_dados import Base


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(150), nullable=False)

    # Código único usado para identificar cada produto no estoque.
    sku = Column(String(50), unique=True, nullable=False, index=True)

    descricao = Column(String(255), nullable=True)


    preco_custo = Column(Numeric(10, 2), nullable=False)
    preco_venda = Column(Numeric(10, 2), nullable=False)

    quantidade_estoque = Column(Integer, nullable=False, default=0)
    estoque_minimo = Column(Integer, nullable=False, default=5)

    data_cadastro = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

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
