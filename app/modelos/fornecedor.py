
from sqlalchemy import Column, Integer, String

from app.banco_de_dados import Base


class Fornecedor(Base):
    __tablename__ = "fornecedores"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(150), nullable=False)

    # Identificador fiscal do fornecedor; cada fornecedor deve ter um CNPJ exclusivo.
    cnpj = Column(String(18), nullable=False, unique=True, index=True)

    email = Column(String(150), unique=True, nullable=True)

    telefone = Column(String(20), nullable=True)
