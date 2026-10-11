from fastapi import APIRouter, Depends, HTTPException,status
from sqlalchemy.orm import Session

from app.banco_de_dados import obter_sessao
from app.modelos.categoria import Categoria
from app.esquemas.categoria import CategoriaCriacao, CategoriaResposta



router = APIRouter(
    prefix="/categorias",
    tags=["Categorias"],
)


@router.get("/", response_model=list[CategoriaResposta])
def listar_categorias(
    sessao: Session = Depends(obter_sessao),
):
    categorias = sessao.query(Categoria).all()
    return categorias


@router.post(
    "/",
    response_model=CategoriaResposta,
    status_code=status.HTTP_201_CREATED,
)
def criar_categoria(
    dados: CategoriaCriacao,
    sessao: Session = Depends(obter_sessao),
):
    categoria = Categoria(
        nome=dados.nome,
        descricao=dados.descricao,
    )

    sessao.add(categoria)
    sessao.commit()
    sessao.refresh(categoria)

    return categoria


@router.get("/{categoria_id}", response_model=CategoriaResposta)
def buscar_categoria(
    categoria_id: int,
    sessao: Session = Depends(obter_sessao),
):
    categoria = sessao.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if categoria is None:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada",
        )

    return categoria


@router.put("/{categoria_id}", response_model=CategoriaResposta)
def atualizar_categoria(
    categoria_id: int,
    dados: CategoriaCriacao,
    sessao: Session = Depends(obter_sessao),
):
    categoria = sessao.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada",
        )

    categoria.nome = dados.nome
    categoria.descricao = dados.descricao

    sessao.commit()
    sessao.refresh(categoria)

    return categoria


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_categoria(
    categoria_id: int,
    sessao: Session = Depends(obter_sessao),
):
    categoria = sessao.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if categoria is None:
        raise HTTPException(
            status_code=404,
            detail="Categoria não encontrada",
        )

    sessao.delete(categoria)
    sessao.commit()
