
import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.rotas.categorias import router as categorias_router
from app.rotas.fornecedores import router as fornecedores_router
from app.rotas.produtos import router as produtos_router
from app.rotas.movimentacoes_estoque import (
    router as movimentacoes_estoque_router,
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Gerenciamento de Estoque",
    description=(
        "API para gerenciar produtos, fornecedores, "
        "categorias e movimentações de estoque."
    ),
    version="1.0.0",
)


@app.exception_handler(HTTPException)
async def tratar_erro_http(
    request: Request,
    exc: HTTPException,
) -> JSONResponse:
    """Padroniza erros HTTP mantendo o status original."""
    mensagem = (
        exc.detail
        if isinstance(exc.detail, str)
        else "A requisição não pôde ser processada."
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "erro": {
                "codigo": exc.status_code,
                "mensagem": mensagem,
            }
        },
        headers=exc.headers,
    )


@app.exception_handler(RequestValidationError)
async def tratar_erro_validacao(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    """Padroniza erros de validação dos dados recebidos."""
    return JSONResponse(
        status_code=400,
        content={
            "erro": {
                "codigo": 400,
                "mensagem": (
                    "Dados inválidos na requisição. "
                    "Verifique os campos enviados."
                ),
            }
        },
    )


@app.exception_handler(Exception)
async def tratar_erro_interno(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """Registra erros inesperados sem expor detalhes internos."""
    logger.error(
        "Erro inesperado ao processar %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )

    return JSONResponse(
        status_code=500,
        content={
            "erro": {
                "codigo": 500,
                "mensagem": (
                    "Ocorreu um erro interno no servidor. "
                    "Tente novamente mais tarde."
                ),
            }
        },
    )


app.include_router(categorias_router)
app.include_router(fornecedores_router)
app.include_router(produtos_router)
app.include_router(movimentacoes_estoque_router)


@app.get("/")
def pagina_inicial():
    return {
        "mensagem": "API de gerenciamento de estoque funcionando!"
    }
