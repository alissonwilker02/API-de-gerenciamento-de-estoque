from datetime import date, datetime, time, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.banco_de_dados import obter_sessao
from app.esquemas.movimentacao_estoque import (
    MovimentacaoEstoqueCriacao,
    MovimentacaoEstoqueResposta,
)
from app.modelos.fornecedor import Fornecedor
from app.modelos.movimentacao_estoque import MovimentacaoEstoque
from app.modelos.produto import Produto

router = APIRouter(
    prefix="/movimentacoes-estoque",
    tags=["Movimentações de Estoque"],
)


@router.post(
    "/",
    response_model=MovimentacaoEstoqueResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_movimentacao(
    dados: MovimentacaoEstoqueCriacao,
    sessao: Session = Depends(obter_sessao),
):
    produto = (
        sessao.query(Produto)
        .filter(Produto.id == dados.produto_id)
        .first()
    )

    if produto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )

    if dados.tipo == "saida":
        if produto.quantidade_estoque < dados.quantidade:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Estoque insuficiente para essa saída",
            )

        produto.quantidade_estoque -= dados.quantidade
    else:
        produto.quantidade_estoque += dados.quantidade

    movimentacao = MovimentacaoEstoque(
        produto_id=dados.produto_id,
        tipo=dados.tipo,
        quantidade=dados.quantidade,
        observacao=dados.observacao,
    )

    sessao.add(movimentacao)
    sessao.commit()
    sessao.refresh(movimentacao)

    return movimentacao



@router.get(
    "/",
    response_model=list[MovimentacaoEstoqueResposta],
)
def listar_movimentacoes(
    produto_id: int | None = None,
    fornecedor_id: int | None = None,
    tipo: Literal["entrada", "saida"] | None = None,
    data_inicio: date | None = None,
    data_fim: date | None = None,
    sessao: Session = Depends(obter_sessao),
):
    consulta = sessao.query(MovimentacaoEstoque)

    # Valida se o fornecedor informado existe.
    if fornecedor_id is not None:
        fornecedor = (
            sessao.query(Fornecedor)
            .filter(Fornecedor.id == fornecedor_id)
            .first()
        )

        if fornecedor is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Fornecedor não encontrado",
            )

    # Filtra pela data inicial.
    if data_inicio is not None:
        inicio = datetime.combine(data_inicio, time.min)

        consulta = consulta.filter(
            MovimentacaoEstoque.data_movimentacao >= inicio
        )

    # Inclui todo o dia final no período pesquisado.
    if data_fim is not None:
        dia_seguinte = datetime.combine(
            data_fim + timedelta(days=1),
            time.min,
        )

        consulta = consulta.filter(
            MovimentacaoEstoque.data_movimentacao < dia_seguinte
        )

    # Filtra pelo produto.
    if produto_id is not None:
        consulta = consulta.filter(
            MovimentacaoEstoque.produto_id == produto_id
        )

    # Filtra pelo fornecedor do produto associado.
    if fornecedor_id is not None:
        consulta = consulta.join(
            Produto,
            MovimentacaoEstoque.produto_id == Produto.id,
        ).filter(
            Produto.fornecedor_id == fornecedor_id
        )

    # Filtra pelo tipo de movimentação.
    if tipo is not None:
        consulta = consulta.filter(
            MovimentacaoEstoque.tipo == tipo
        )

    # Retorna as movimentações mais recentes primeiro.
    movimentacoes = (
        consulta
        .order_by(MovimentacaoEstoque.data_movimentacao.desc())
        .all()
    )

    return movimentacoes