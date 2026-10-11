
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.banco_de_dados import obter_sessao
from app.modelos.fornecedor import Fornecedor
from app.esquemas.fornecedor import (
    FornecedorCriacao,
    FornecedorResposta,
)

router = APIRouter(
    prefix="/fornecedores",
    tags=["Fornecedores"],
)

@router.get("/", response_model=list[FornecedorResposta])
def listar_fornecedores(
    sessao: Session = Depends(obter_sessao),
):
    fornecedores = sessao.query(Fornecedor).all()
    return fornecedores

@router.post(
    "/",
    response_model=FornecedorResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_fornecedor(
    dados: FornecedorCriacao,
    sessao: Session = Depends(obter_sessao),
):
    fornecedor = Fornecedor(
        nome=dados.nome,
        email=dados.email,
        telefone=dados.telefone,
    )

    sessao.add(fornecedor)
    sessao.commit()
    sessao.refresh(fornecedor)

    return fornecedor


@router.get(
    "/{fornecedor_id}",
    response_model=FornecedorResposta,
)
def buscar_fornecedor(
    fornecedor_id: int,
    sessao: Session = Depends(obter_sessao),
):
    fornecedor = sessao.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id
    ).first()

    if fornecedor is None:
        raise HTTPException(
            status_code=404,
            detail="Fornecedor não encontrado",
        )

    return fornecedor


@router.put(
    "/{fornecedor_id}",
    response_model=FornecedorResposta,
)
def atualizar_fornecedor(
    fornecedor_id: int,
    dados: FornecedorCriacao,
    sessao: Session = Depends(obter_sessao),
):
    fornecedor = sessao.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id
    ).first()

    if fornecedor is None:
        raise HTTPException(
            status_code=404,
            detail="Fornecedor não encontrado",
        )

    fornecedor.nome = dados.nome
    fornecedor.email = dados.email
    fornecedor.telefone = dados.telefone

    sessao.commit()
    sessao.refresh(fornecedor)

    return fornecedor


@router.delete(
    "/{fornecedor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_fornecedor(
    fornecedor_id: int,
    sessao: Session = Depends(obter_sessao),
):
    fornecedor = sessao.query(Fornecedor).filter(
        Fornecedor.id == fornecedor_id
    ).first()

    if fornecedor is None:
        raise HTTPException(
            status_code=404,
            detail="Fornecedor não encontrado",
        )

    sessao.delete(fornecedor)
    sessao.commit()
