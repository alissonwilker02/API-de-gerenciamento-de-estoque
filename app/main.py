import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.rotas.categorias import router as categorias_router
from app.rotas.fornecedores import router as fornecedores_router
from app.rotas.produtos import router as produtos_router
from app.rotas.movimentacoes_estoque import (
    router as movimentacoes_estoque_router,
)

# Registra erros inesperados no terminal do servidor.
logger = logging.getLogger(__name__)

app = FastAPI(
    title="API de Gerenciamento de Estoque",
    description=(
        "API para gerenciar produtos, fornecedores, "
        "categorias e movimentações de estoque."
    ),
    version="1.0.0",
)


@app.exception_handler(Exception)
async def tratar_erro_interno(
    request: Request,
    exc: Exception,
) -> JSONResponse:
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
