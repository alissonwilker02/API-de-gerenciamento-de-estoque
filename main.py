from fastapi import FastAPI

#Cria a aplicação principal da API

app = FastAPI(
    title="API de Gerenciamento de Estoques",
    description="API desenvolvida para o desafio técnico da Ecomp Jr",
    version="0.1.0",
)

@app.get("/")
def home():
    return {
        "mensagem": "API de gerenciamento de estoque funcionando!",
        "status": "online",
    }