
from fastapi import FastAPI

app = FastAPI(
    title="API de Gerenciamento de Estoque",
    description="API para gerenciar produtos, fornecedores, categorias e movimentações de estoque.",
    version="1.0.0",
)


@app.get("/")
def pagina_inicial():
    return {
        "mensagem": "API de gerenciamento de estoque funcionando!"
    }
