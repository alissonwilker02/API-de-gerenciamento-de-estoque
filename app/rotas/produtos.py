
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.banco_de_dados import obter_sessao
from app.modelos.produto import Produto
from app.esquemas.produto import ProdutoCriacao, ProdutoResposta


router = APIRouter(
    prefix="/produtos",
    tags=["Produtos"],
)


@router.get("/", response_model=list[ProdutoResposta])
def listar_produtos(
    sessao: Session = Depends(obter_sessao),
):
    produtos = sessao.query(Produto).all()
    return produtos


@router.post(
    "/",
    response_model=ProdutoResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_produto(
    dados: ProdutoCriacao,
    sessao: Session = Depends(obter_sessao),
):
    produto = Produto(
        nome=dados.nome,
        descricao=dados.descricao,
        preco=dados.preco,
        quantidade_estoque=dados.quantidade_estoque,
        estoque_minimo=dados.estoque_minimo,
        categoria_id=dados.categoria_id,
        fornecedor_id=dados.fornecedor_id,
    )

    sessao.add(produto)
    sessao.commit()
    sessao.refresh(produto)

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
            status_code=404,
            detail="Produto não encontrado",
        )

    return produto


@router.put(
    "/{produto_id}",
    response_model=ProdutoResposta,
)
def atualizar_produto(
    produto_id: int,
    dados: ProdutoCriacao,
    sessao: Session = Depends(obter_sessao),
):
    produto = sessao.query(Produto).filter(
        Produto.id == produto_id
    ).first()

    if produto is None:
        raise HTTPException(
            status_code=404,
            detail="Produto não encontrado",
        )

    produto.nome = dados.nome
    produto.descricao = dados.descricao
    produto.preco = dados.preco
    produto.quantidade_estoque = dados.quantidade_estoque
    produto.estoque_minimo = dados.estoque_minimo
    produto.categoria_id = dados.categoria_id
    produto.fornecedor_id = dados.fornecedor_id

    sessao.commit()
    sessao.refresh(produto)

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
            detail="Produto não encontrado",
        )

    sessao.delete(produto)
    sessao.commit()

    return None
