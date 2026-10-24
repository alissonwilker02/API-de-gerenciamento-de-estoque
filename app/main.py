
import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.esquemas.erro import ErroResposta
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


@app.exception_handler(StarletteHTTPException)
async def tratar_erro_http(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    """Padroniza erros da API e do framework, preservando status e headers."""
    mensagem = (
        exc.detail
        if isinstance(exc.detail, str)
        else "A requisição não pôde ser processada."
    )
    if exc.status_code == 404 and mensagem == "Not Found":
        mensagem = "Rota não encontrada."

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
    """Converte falhas de validação para o contrato HTTP 400 da API."""
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
    """Registra detalhes no servidor sem expô-los na resposta ao cliente."""
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


def gerar_openapi() -> dict[str, Any]:
    """Mantém a documentação alinhada ao formato e status dos erros reais."""
    if app.openapi_schema:
        return app.openapi_schema

    esquema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    componentes = esquema.setdefault("components", {}).setdefault(
        "schemas", {}
    )
    definicao_erro = ErroResposta.model_json_schema(
        ref_template="#/components/schemas/{model}"
    )

    for nome, definicao in definicao_erro.pop("$defs", {}).items():
        componentes[nome] = definicao
    componentes["ErroResposta"] = definicao_erro

    # O FastAPI documenta validações como 422 por padrão; a API responde 400.
    for caminho in esquema["paths"].values():
        for operacao in caminho.values():
            respostas = operacao.get("responses")
            if not respostas or "422" not in respostas:
                continue

            respostas.pop("422")
            respostas["400"] = {
                "description": "Dados inválidos na requisição.",
                "content": {
                    "application/json": {
                        "schema": {
                            "$ref": "#/components/schemas/ErroResposta"
                        }
                    }
                },
            }

    app.openapi_schema = esquema
    return app.openapi_schema


app.openapi = gerar_openapi


app.include_router(categorias_router)
app.include_router(fornecedores_router)
app.include_router(produtos_router)
app.include_router(movimentacoes_estoque_router)


@app.get("/")
def pagina_inicial():
    return {
        "mensagem": "API de gerenciamento de estoque funcionando!"
    }
