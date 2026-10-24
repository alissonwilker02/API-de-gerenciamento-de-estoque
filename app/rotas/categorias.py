from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
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

    try:
        sessao.add(categoria)
        sessao.commit()
        sessao.refresh(categoria)

    except IntegrityError:
        sessao.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma categoria com esse nome.",
        )

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
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada.",
        )

    nome_existente = sessao.query(Categoria).filter(
        Categoria.nome == dados.nome,
        Categoria.id != categoria_id,
    ).first()

    if nome_existente is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe outra categoria com esse nome.",
        )

    categoria.nome = dados.nome
    categoria.descricao = dados.descricao

    try:
        sessao.commit()
        sessao.refresh(categoria)
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não foi possível atualizar a categoria devido a um conflito de dados.",
        )

    return categoria




@router.delete(
    "/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def excluir_categoria(
    categoria_id: int,
    sessao: Session = Depends(obter_sessao),
):
    categoria = sessao.query(Categoria).filter(
        Categoria.id == categoria_id
    ).first()

    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada.",
        )

    try:
        sessao.delete(categoria)
        sessao.commit()
    except IntegrityError:
        sessao.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Não é possível excluir a categoria porque existem produtos associados a ela.",
        )

    return None