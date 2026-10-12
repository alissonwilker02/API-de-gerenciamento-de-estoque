from datetime import date, datetime, time, timedelta
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.banco_de_dados import obter_sessao
from app.esquemas.movimentacao_estoque import (
    MovimentacaoEstoqueCriacao,
    MovimentacaoEstoqueResposta,
)
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
    produto = sessao.query(Produto).filter(
        Produto.id == dados.produto_id
    ).first()

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
    tipo: Literal["entrada", "saida"] | None = None,
    sessao: Session = Depends(obter_sessao),
    data_inicio: date | None = None,
    data_fim: date | None = None,
):
    consulta = sessao.query(MovimentacaoEstoque)
    if data_inicio is not None:
        inicio = datetime.combine(data_inicio, time.min)

        consulta = consulta.filter(
            MovimentacaoEstoque.data_movimentacao >= inicio
        )

    if data_fim is not None:
        dia_seguinte = datetime.combine(
            data_fim + timedelta(days=1),
            time.min,
        )

        consulta = consulta.filter(
            MovimentacaoEstoque.data_movimentacao < dia_seguinte
        )

    if produto_id is not None:
        consulta = consulta.filter(
            MovimentacaoEstoque.produto_id == produto_id
        )

    if tipo is not None:
        consulta = consulta.filter(
            MovimentacaoEstoque.tipo == tipo
        )

    movimentacoes = (
        consulta
        .order_by(MovimentacaoEstoque.data_movimentacao.desc())
        .all()
    )

    return movimentacoes