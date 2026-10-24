
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.banco_de_dados import obter_sessao
from app.modelos.categoria import Categoria
from app.modelos.fornecedor import Fornecedor
from app.modelos.produto import Produto
from app.esquemas.produto import (
    ProdutoAtualizacao,
    ProdutoCriacao,
    ProdutoResposta,
)


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
)


def validar_relacionamentos(
    sessao: Session,
    categoria_id: int,
    fornecedor_id: int,
) -> None:
    """Garante que as referências existem antes de criar ou alterar produto."""
    categoria = sessao.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada.",
        )

    fornecedor = sessao.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id
    ).first()

    if fornecedor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado.",
        )


@router.get("/", response_model=list[ProdutoResposta])
def listar_produtos(
    sessao: Session = Depends(obter_sessao),
):
    return sessao.query(Produto).all()


@router.get(
    "/estoque-baixo",
    response_model=list[ProdutoResposta],
)
def listar_produtos_estoque_baixo(
    sessao: Session = Depends(obter_sessao),
):
    # Inclui produtos no limite mínimo, além dos que já estão abaixo dele.
    return (
        sessao.query(Produto)
        .filter(
            Produto.quantidade_estoque <= Produto.estoque_minimo
        )
        .all()
    )


@router.post(
    "/",
    response_model=ProdutoResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_produto(
    dados: ProdutoCriacao,
    sessao: Session = Depends(obter_sessao),
):
    validar_relacionamentos(
        sessao,
        dados.categoria_id,
        dados.fornecedor_id,
    )

    sku_existente = sessao.query(Produto).filter(
        Produto.sku == dados.sku
    ).first()

    if sku_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um produto com esse SKU.",
        )

    produto = Produto(
        nome=dados.nome,
        sku=dados.sku,
        descricao=dados.descricao,
        preco_custo=dados.preco_custo,
        preco_venda=dados.preco_venda,
        # O saldo inicial só pode ser alterado por movimentações registradas.
        quantidade_estoque=0,
        estoque_minimo=dados.estoque_minimo,
        categoria_id=dados.categoria_id,
        fornecedor_id=dados.fornecedor_id,
    )

    try:
        sessao.add(produto)
        sessao.commit()
        sessao.refresh(produto)
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar o produto devido a um conflito de dados.",
        )

    return produto


@router.get(
    "/{produto_id}",
    response_model=ProdutoResposta,
)
def buscar_produto(
    produto_id: int,
    sessao: Session = Depends(obter_sessao),
):
    produto = sessao.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    return produto


@router.put(
    "/{produto_id}",
    response_model=ProdutoResposta,
)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoAtualizacao,
    sessao: Session = Depends(obter_sessao),
):
    produto = sessao.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    validar_relacionamentos(
        sessao,
        dados.categoria_id,
        dados.fornecedor_id,
    )

    sku_existente = sessao.query(Produto).filter(
        Produto.sku == dados.sku,
        Produto.id != produto_id,
    ).first()

    if sku_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outro produto com esse SKU.",
        )

    # A atualização cadastral não altera o saldo de estoque do produto.
    produto.nome = dados.nome
    produto.sku = dados.sku
    produto.descricao = dados.descricao
    produto.preco_custo = dados.preco_custo
    produto.preco_venda = dados.preco_venda
    produto.estoque_minimo = dados.estoque_minimo
    produto.categoria_id = dados.categoria_id
    produto.fornecedor_id = dados.fornecedor_id

    try:
        sessao.commit()
        sessao.refresh(produto)
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar o produto devido a um conflito de dados.",
        )

    return produto


@router.delete(
    "/{produto_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_produto(
    produto_id: int,
    sessao: Session = Depends(obter_sessao),
):
    produto = sessao.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado.",
        )

    sessao.delete(produto)

    try:
        sessao.commit()
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir o produto porque existem movimentações associadas a ele.",
        )

    return None
