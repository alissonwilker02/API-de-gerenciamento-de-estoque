from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
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
    fornecedor_existente = sessao.query(Fornecedor).filter(
        Fornecedor.cnpj == dados.cnpj
    ).first()

    if fornecedor_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um fornecedor com esse CNPJ.",
        )

    fornecedor = Fornecedor(
        nome=dados.nome,
        cnpj=dados.cnpj,
        email=dados.email,
        telefone=dados.telefone,
    )

    try:
        sessao.add(fornecedor)
        sessao.commit()
        sessao.refresh(fornecedor)
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível cadastrar o fornecedor devido a um conflito de dados.",
        )

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado.",
        )

    cnpj_existente = sessao.query(Fornecedor).filter(
        Fornecedor.cnpj == dados.cnpj,
        Fornecedor.id != fornecedor_id,
    ).first()

    if cnpj_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outro fornecedor com esse CNPJ.",
        )

    fornecedor.nome = dados.nome
    fornecedor.cnpj = dados.cnpj
    fornecedor.email = dados.email
    fornecedor.telefone = dados.telefone

    try:
        sessao.commit()
        sessao.refresh(fornecedor)
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar o fornecedor devido a um conflito de dados.",
        )

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fornecedor não encontrado.",
        )

    try:
        sessao.delete(fornecedor)
        sessao.commit()
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir o fornecedor porque existem produtos associados a ele.",
        )

    return None
