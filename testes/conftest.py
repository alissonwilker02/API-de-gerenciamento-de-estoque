
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.banco_de_dados import Base, obter_sessao

# Importar os modelos garante que suas tabelas sejam registradas
# no metadata do SQLAlchemy antes de criar o banco.
from app.modelos.categoria import Categoria
from app.modelos.fornecedor import Fornecedor
from app.modelos.produto import Produto
from app.modelos.movimentacao_estoque import MovimentacaoEstoque


@pytest.fixture
def cliente():
    # Cria um banco SQLite em memória para os testes.
    motor_teste = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Habilita a verificação de chaves estrangeiras no SQLite.
    # Sem isso, o SQLite pode permitir a exclusão de um fornecedor
    # mesmo quando existem produtos associados a ele.
    @event.listens_for(motor_teste, "connect")
    def habilitar_chaves_estrangeiras(conexao, registro):
        cursor = conexao.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Cria uma fábrica de sessões para o banco de teste.
    SessaoTeste = sessionmaker(
        bind=motor_teste,
        autocommit=False,
        autoflush=False,
    )

    # Cria as tabelas antes de executar os testes.
    Base.metadata.create_all(bind=motor_teste)

    # Substitui a sessão do banco real pela sessão de teste.
    def obter_sessao_teste():
        sessao = SessaoTeste()
        try:
            yield sessao
        finally:
            sessao.close()

    app.dependency_overrides[obter_sessao] = obter_sessao_teste

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        # Restaura as dependências e limpa o banco de teste.
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=motor_teste)
        motor_teste.dispose()
