from fastapi import FastAPI
from app.rotas.categorias import router as categorias_router
from app.rotas.fornecedores import router as fornecedores_router
from app.rotas.produtos import router as produtos_router
from app.rotas.movimentacoes_estoque import (
    router as movimentacoes_estoque_router,
)

app = FastAPI(
    title="API de Gerenciamento de Estoque",
    description="API para gerenciar produtos, fornecedores, categorias e movimentações de estoque.",
    version="1.0.0",
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
