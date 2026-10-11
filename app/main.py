from fastapi import FastAPI
from app.rotas.categorias import router as categorias_router

app = FastAPI(
    title="API de Gerenciamento de Estoque",
    description="API para gerenciar produtos, fornecedores, categorias e movimentações de estoque.",
    version="1.0.0",
)

app.include_router(categorias_router)


@app.get("/")
def pagina_inicial():
    return {
        "mensagem": "API de gerenciamento de estoque funcionando!"
    }
