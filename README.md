# API de Gerenciamento de Estoque

API REST desenvolvida em Python com FastAPI e PostgreSQL para gerenciar produtos, fornecedores, categorias e movimentações de estoque. O projeto foi desenvolvido como parte do Desafio Técnico da Trilha Back-End do Processo Seletivo EcompJr 2026.2.

## Funcionalidades

- Cadastro, consulta, atualização e exclusão de categorias.
- Cadastro, consulta, atualização e exclusão de fornecedores.
- Cadastro, consulta, atualização e exclusão de produtos.
- Associação de produtos às suas categorias e fornecedores.
- Registro e consulta do histórico de movimentações de estoque.
- Atualização automática do estoque após entradas e saídas.
- Bloqueio de saídas em quantidade superior ao estoque disponível.
- Consulta de produtos com estoque baixo.
- Filtragem de movimentações por produto, fornecedor, tipo e período.
- Validação dos dados e tratamento de erros HTTP.

## Tecnologias utilizadas

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- Pytest
- HTTPX

## Estrutura do projeto

```text
desafio_ecompjr/
├── app/
│   ├── esquemas/
│   ├── modelos/
│   ├── rotas/
│   ├── servicos/
│   ├── banco_de_dados.py
│   └── main.py
├── migracoes/
├── testes/
│   ├── conftest.py
│   └── test_api.py
├── .env
├── .gitignore
├── alembic.ini
├── requirements.txt
└── README.md
```

**Responsabilidade das principais pastas:**

- `app/modelos/`: entidades e relacionamentos do banco de dados.
- `app/esquemas/`: validação e estrutura dos dados de entrada e saída.
- `app/rotas/`: endpoints e regras de acesso à API.
- `app/banco_de_dados.py`: configuração da conexão e das sessões do banco.
- `migracoes/`: histórico de alterações do esquema do banco de dados.
- `testes/`: testes automatizados da API.

## Pré-requisitos

Antes de iniciar, instale:

- Python compatível com as dependências do projeto.
- PostgreSQL.
- Git.

## Instalação e configuração

### 1. Clone o repositório

```bash
git clone https://github.com/alissonwilker02/API-de-gerenciamento-de-estoque.git
cd API-de-gerenciamento-de-estoque
```

### 2. Crie e ative o ambiente virtual

No Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Instale as dependências

```bash
python -m pip install -r requirements.txt
```

### 4. Configure o PostgreSQL

Crie um banco de dados PostgreSQL para a aplicação.

Na raiz do projeto, crie um arquivo `.env` com as variáveis utilizadas pela configuração do banco:

```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=estoque_ecompjr
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
```

Substitua os valores pelos dados do seu ambiente. O nome do banco e a porta devem corresponder à sua configuração local.

**Importante:** não compartilhe credenciais reais nem envie o arquivo `.env` para o GitHub.

### 5. Execute as migrações

Com o banco criado e as variáveis de ambiente configuradas, execute:

```bash
alembic upgrade head
```

Esse comando aplica as migrações pendentes e prepara a estrutura do banco de dados.

### 6. Inicie a API

```bash
uvicorn app.main:app --reload
```

Por padrão, a aplicação estará disponível em:

- API: http://127.0.0.1:8000
- Documentação interativa: http://127.0.0.1:8000/docs
- Documentação OpenAPI: http://127.0.0.1:8000/openapi.json

## Endpoints

A documentação interativa em `/docs` apresenta os métodos, parâmetros, esquemas e respostas registrados pela aplicação.

### Categorias

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/categorias/` | Lista categorias |
| POST | `/categorias/` | Cadastra uma categoria |
| GET | `/categorias/{categoria_id}` | Consulta uma categoria |
| PUT | `/categorias/{categoria_id}` | Atualiza uma categoria |
| DELETE | `/categorias/{categoria_id}` | Exclui uma categoria |

Exemplo de cadastro:

```json
{
  "nome": "Eletrônicos",
  "descricao": "Produtos eletrônicos"
}
```

### Fornecedores

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/fornecedores/` | Lista fornecedores |
| POST | `/fornecedores/` | Cadastra um fornecedor |
| GET | `/fornecedores/{fornecedor_id}` | Consulta um fornecedor |
| PUT | `/fornecedores/{fornecedor_id}` | Atualiza um fornecedor |
| DELETE | `/fornecedores/{fornecedor_id}` | Exclui um fornecedor |

Exemplo de cadastro:

```json
{
  "nome": "Fornecedor Exemplo",
  "cnpj": "11222333000181",
  "email": "contato@exemplo.com",
  "telefone": "75999999999"
}
```

O CNPJ deve atender às validações implementadas pela aplicação, e o e-mail e o CNPJ não podem estar duplicados.

### Produtos

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/produtos/` | Lista produtos |
| POST | `/produtos/` | Cadastra um produto |
| GET | `/produtos/estoque-baixo` | Lista produtos com estoque baixo |
| GET | `/produtos/{produto_id}` | Consulta um produto |
| PUT | `/produtos/{produto_id}` | Atualiza um produto |
| DELETE | `/produtos/{produto_id}` | Exclui um produto |

Exemplo de cadastro:

```json
{
  "nome": "Teclado USB",
  "sku": "TEC-001",
  "descricao": "Teclado USB padrão",
  "preco_custo": 50.00,
  "preco_venda": 89.90,
  "estoque_minimo": 5,
  "categoria_id": 1,
  "fornecedor_id": 1
}
```

O produto é cadastrado com estoque inicial zero. As alterações de quantidade são realizadas por meio das movimentações de estoque.

### Movimentações de estoque

As movimentações registram entradas e saídas de produtos, mantendo um histórico para auditoria. Cada movimentação atualiza automaticamente a quantidade disponível no estoque. Os registros podem ser criados e consultados, mas não possuem endpoints de edição ou exclusão.

| Método | Endpoint | Descrição |
|---|---|---|
| POST | `/movimentacoes-estoque/` | Registra uma entrada ou saída |
| GET | `/movimentacoes-estoque/` | Lista e filtra as movimentações |

#### Exemplo de entrada

```json
{
  "produto_id": 1,
  "tipo": "entrada",
  "quantidade": 10,
  "observacao": "Reposição de estoque"
}
```

#### Exemplo de saída

```json
{
  "produto_id": 1,
  "tipo": "saida",
  "quantidade": 2,
  "observacao": "Saída de produtos"
}
```

#### Exemplo de resposta — movimentação criada (HTTP 201)

```json
{
  "id": 1,
  "produto_id": 1,
  "tipo": "entrada",
  "quantidade": 10,
  "observacao": "Reposição de estoque",
  "data_movimentacao": "2026-10-24T10:30:00"
}
```

O campo id identifica a movimentação registrada, enquanto data_movimentacao informa quando ela foi criada. Os valores acima são apenas ilustrativos.

O campo `tipo` aceita `entrada` ou `saida`. A quantidade deve ser positiva. Uma saída maior que o estoque disponível é rejeitada.

#### Parâmetros de consulta

Todos os parâmetros abaixo são opcionais e podem ser combinados.

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `produto_id` | Inteiro | Filtra pelo identificador do produto |
| `fornecedor_id` | Inteiro | Filtra pelo fornecedor associado ao produto |
| `tipo` | Texto | Filtra por `entrada` ou `saida` |
| `data_inicio` | Data | Inclui movimentações a partir do início do dia informado |
| `data_fim` | Data | Inclui movimentações até o final do dia informado |

As datas devem ser informadas no formato `AAAA-MM-DD`.

Exemplo: consultar as saídas do fornecedor 1 entre 1º e 31 de outubro de 2026:

```http
GET /movimentacoes-estoque/?fornecedor_id=1&tipo=saida&data_inicio=2026-10-01&data_fim=2026-10-31
```

Se o fornecedor informado não existir, a API retorna `404`. Caso a saída solicitada exceda o estoque disponível, retorna `400`.


## Tratamento de erros

A API retorna os erros no formato padronizado abaixo, sem expor detalhes
internos ou stack traces:

```json
{
  "erro": {
    "codigo": 404,
    "mensagem": "Produto não encontrado."
  }
}
```

O campo `codigo` corresponde ao status HTTP. Validações de entrada retornam
`400` (inclusive na documentação OpenAPI); recursos inexistentes retornam
`404`, conflitos de negócio retornam `409` e falhas inesperadas retornam
`500`. Erros de rotas inexistentes também seguem esse formato.

Entre os códigos utilizados estão:

| Código | Significado |
|---|---|
| 200 | Requisição executada com sucesso |
| 201 | Recurso criado |
| 204 | Recurso excluído sem conteúdo de resposta |
| 400 | Operação inválida segundo uma regra de negócio |
| 404 | Recurso não encontrado |
| 409 | Conflito com dados ou relacionamentos existentes |
| 500 | Erro interno inesperado |

As mensagens explicam a falha sem incluir informações sensíveis do servidor.

## Testes automatizados

Os testes automatizados verificam as principais funcionalidades, regras de negócio e validações da API.

Para executar a suíte:

```bash
python -m pytest -v
```

Para medir a cobertura do código:

```bash
python -m pytest --cov=app --cov-report=term-missing -v
```

A suíte atual possui 69 testes aprovados e 93% de cobertura, medidos com
`pytest-cov`.

Os testes utilizam uma configuração de banco isolada para evitar dependência dos dados do PostgreSQL de desenvolvimento.

## Controle de versão

O projeto utiliza Git e GitHub para controle de versão e acompanhamento das alterações.

Repositório: https://github.com/alissonwilker02/API-de-gerenciamento-de-estoque
