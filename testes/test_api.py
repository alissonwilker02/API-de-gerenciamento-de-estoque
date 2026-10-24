
def criar_categoria(cliente, nome="Eletrônicos"):
    resposta = cliente.post(
        "/categorias/",
        json={"nome": nome, "descricao": "Categoria de teste"},
    )
    assert resposta.status_code == 201
    return resposta.json()



def criar_fornecedor(
    cliente,
    cnpj="12345678000199",
    email="fornecedor@example.com",
    nome="Fornecedor Teste",
):
    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": nome,
            "cnpj": cnpj,
            "email": email,
            "telefone": "71999999999",
        },
    )

    assert resposta.status_code == 201, resposta.text
    return resposta.json()



def criar_produto(cliente, categoria_id, fornecedor_id, sku="MOUSE-001"):
    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": sku,
            "descricao": "Mouse para teste",
            "preco_custo": "30.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria_id,
            "fornecedor_id": fornecedor_id,
        },
    )
    assert resposta.status_code == 201
    return resposta.json()


# -------------------------
# CATEGORIAS
# -------------------------

def test_criar_e_listar_categoria(cliente):
    categoria = criar_categoria(cliente)

    resposta = cliente.get("/categorias/")

    assert resposta.status_code == 200
    assert any(item["id"] == categoria["id"] for item in resposta.json())


def test_buscar_categoria_inexistente(cliente):
    resposta = cliente.get("/categorias/99999")

    assert resposta.status_code == 404


def test_categoria_duplicada(cliente):
    criar_categoria(cliente)

    resposta = cliente.post(
        "/categorias/",
        json={"nome": "Eletrônicos", "descricao": "Duplicada"},
    )

    assert resposta.status_code == 409


# -------------------------
# FORNECEDORES
# -------------------------

def test_criar_fornecedor(cliente):
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.get(f"/fornecedores/{fornecedor['id']}")

    assert resposta.status_code == 200
    assert resposta.json()["cnpj"] == "12345678000199"


def test_cnpj_invalido(cliente):
    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": "Fornecedor Inválido",
            "cnpj": "11111111111111",
            "email": "invalido@example.com",
            "telefone": "71999999999",
        },
    )

    assert resposta.status_code == 422


def test_cnpj_duplicado(cliente):
    criar_fornecedor(cliente)

    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": "Outro Fornecedor",
            "cnpj": "12345678000199",
            "email": "outro@example.com",
            "telefone": "71888888888",
        },
    )

    assert resposta.status_code == 409


# -------------------------
# PRODUTOS
# -------------------------

def test_criar_produto_com_estoque_inicial_zero(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    assert produto["quantidade_estoque"] == 0
    assert produto["sku"] == "MOUSE-001"


def test_produto_com_categoria_inexistente(cliente):
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Teclado",
            "sku": "TEC-001",
            "preco_custo": "40.00",
            "preco_venda": "70.00",
            "estoque_minimo": 5,
            "categoria_id": 99999,
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 404


def test_sku_duplicado(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    criar_produto(cliente, categoria["id"], fornecedor["id"])

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Outro Mouse",
            "sku": "MOUSE-001",
            "preco_custo": "35.00",
            "preco_venda": "55.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 409


def test_produto_aparece_no_estoque_baixo(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    resposta = cliente.get("/produtos/estoque-baixo")

    assert resposta.status_code == 200
    assert any(item["id"] == produto["id"] for item in resposta.json())


# -------------------------
# MOVIMENTAÇÕES DE ESTOQUE
# -------------------------

def test_entrada_atualiza_estoque(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 10,
            "observacao": "Compra de teste",
        },
    )

    assert resposta.status_code == 201

    produto_atualizado = cliente.get(
        f"/produtos/{produto['id']}"
    ).json()

    assert produto_atualizado["quantidade_estoque"] == 10


def test_saida_atualiza_estoque(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 10,
        },
    )

    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "saida",
            "quantidade": 3,
        },
    )

    assert resposta.status_code == 201

    produto_atualizado = cliente.get(
        f"/produtos/{produto['id']}"
    ).json()

    assert produto_atualizado["quantidade_estoque"] == 7


def test_saida_maior_que_estoque_e_rejeitada(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "saida",
            "quantidade": 1,
        },
    )

    assert resposta.status_code == 400

    produto_atualizado = cliente.get(
        f"/produtos/{produto['id']}"
    ).json()

    assert produto_atualizado["quantidade_estoque"] == 0


def test_filtro_movimentacoes_por_fornecedor(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 10,
        },
    )

    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={"fornecedor_id": fornecedor["id"]},
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["produto_id"] == produto["id"]


def test_filtro_por_fornecedor_inexistente(cliente):
    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={"fornecedor_id": 99999},
    )

    assert resposta.status_code == 404
    

from datetime import date


def registrar_movimentacao(
    cliente, produto_id, tipo, quantidade
):
    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto_id,
            "tipo": tipo,
            "quantidade": quantidade,
        },
    )

    assert resposta.status_code == 201
    return resposta.json()


def test_filtrar_movimentacoes_por_tipo(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    registrar_movimentacao(
        cliente, produto["id"], "entrada", 10
    )
    registrar_movimentacao(
        cliente, produto["id"], "saida", 3
    )

    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={"tipo": "entrada"},
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["tipo"] == "entrada"


def test_filtrar_movimentacoes_por_produto(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    produto1 = criar_produto(
        cliente, categoria["id"], fornecedor["id"],
        sku="MOUSE-101",
    )
    produto2 = criar_produto(
        cliente, categoria["id"], fornecedor["id"],
        sku="MOUSE-102",
    )

    registrar_movimentacao(
        cliente, produto1["id"], "entrada", 10
    )
    registrar_movimentacao(
        cliente, produto2["id"], "entrada", 20
    )

    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={"produto_id": produto1["id"]},
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["produto_id"] == produto1["id"]



def test_combinar_filtro_fornecedor_e_tipo(cliente):
    categoria = criar_categoria(cliente)

    fornecedor1 = criar_fornecedor(cliente)

    fornecedor2 = criar_fornecedor(
        cliente,
        cnpj="98765432000198",
        email="outro-fornecedor@example.com",
        nome="Outro Fornecedor",
    )

    produto1 = criar_produto(
        cliente, categoria["id"], fornecedor1["id"],
        sku="PROD-201",
    )

    produto2 = criar_produto(
        cliente, categoria["id"], fornecedor2["id"],
        sku="PROD-202",
    )

    registrar_movimentacao(
        cliente, produto1["id"], "entrada", 10
    )
    registrar_movimentacao(
        cliente, produto1["id"], "saida", 2
    )
    registrar_movimentacao(
    cliente, produto2["id"], "entrada", 5
    )
    registrar_movimentacao(
        cliente, produto2["id"], "saida", 1
    )

    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={
            "fornecedor_id": fornecedor1["id"],
            "tipo": "saida",
        },
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1
    assert resposta.json()[0]["produto_id"] == produto1["id"]
    assert resposta.json()[0]["tipo"] == "saida"


def test_filtro_por_tipo_invalido(cliente):
    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={"tipo": "devolucao"},
    )

    assert resposta.status_code == 422


def test_filtro_por_periodo_sem_resultados(cliente):
    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={"data_inicio": "2099-01-01"},
    )

    assert resposta.status_code == 200
    assert resposta.json() == []


def test_filtro_por_data_fim(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente, categoria["id"], fornecedor["id"]
    )

    registrar_movimentacao(
        cliente, produto["id"], "entrada", 5
    )

    resposta = cliente.get(
        "/movimentacoes-estoque/",
        params={"data_fim": date.today().isoformat()},
    )

    assert resposta.status_code == 200
    assert len(resposta.json()) == 1


def test_movimentacao_com_quantidade_zero(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 0,
        },
    )

    assert resposta.status_code == 422

    # O estoque deve continuar zerado.
    produto_atualizado = cliente.get(
        f"/produtos/{produto['id']}"
    ).json()

    assert produto_atualizado["quantidade_estoque"] == 0


def test_movimentacao_com_quantidade_negativa(cliente):
    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": 1,
            "tipo": "entrada",
            "quantidade": -5,
        },
    )

    assert resposta.status_code == 422


# -------------------------
# ATUALIZAÇÃO E EXCLUSÃO DE CATEGORIAS
# -------------------------

def test_atualizar_categoria(cliente):
    categoria = criar_categoria(cliente)

    resposta = cliente.put(
        f"/categorias/{categoria['id']}",
        json={
            "nome": "Periféricos",
            "descricao": "Mouse, teclado e outros periféricos",
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Periféricos"
    assert resposta.json()["descricao"] == (
        "Mouse, teclado e outros periféricos"
    )

    # Confirma que a alteração foi persistida.
    consulta = cliente.get(f"/categorias/{categoria['id']}")

    assert consulta.status_code == 200
    assert consulta.json()["nome"] == "Periféricos"


def test_atualizar_categoria_inexistente(cliente):
    resposta = cliente.put(
        "/categorias/99999",
        json={
            "nome": "Periféricos",
            "descricao": "Categoria de teste",
        },
    )

    assert resposta.status_code == 404


def test_atualizar_categoria_com_nome_duplicado(cliente):
    criar_categoria(cliente, nome="Eletrônicos")
    segunda = criar_categoria(cliente, nome="Informática")

    resposta = cliente.put(
        f"/categorias/{segunda['id']}",
        json={
            "nome": "Eletrônicos",
            "descricao": "Tentativa de duplicação",
        },
    )

    assert resposta.status_code == 409


def test_excluir_categoria(cliente):
    categoria = criar_categoria(cliente)

    resposta = cliente.delete(
        f"/categorias/{categoria['id']}"
    )

    assert resposta.status_code == 204

    # Depois da exclusão, a categoria não deve ser encontrada.
    consulta = cliente.get(
        f"/categorias/{categoria['id']}"
    )

    assert consulta.status_code == 404


def test_excluir_categoria_inexistente(cliente):
    resposta = cliente.delete("/categorias/99999")

    assert resposta.status_code == 404


# -------------------------
# ATUALIZAÇÃO E EXCLUSÃO DE FORNECEDORES
# -------------------------

def test_atualizar_fornecedor(cliente):
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.put(
        f"/fornecedores/{fornecedor['id']}",
        json={
            "nome": "Fornecedor Atualizado",
            "cnpj": "98765432000198",
            "email": "atualizado@example.com",
            "telefone": "71988887777",
        },
    )

    assert resposta.status_code == 200
    assert resposta.json()["nome"] == "Fornecedor Atualizado"
    assert resposta.json()["cnpj"] == "98765432000198"
    assert resposta.json()["email"] == "atualizado@example.com"
    assert resposta.json()["telefone"] == "71988887777"

    # Confirma que a atualização foi salva no banco.
    consulta = cliente.get(
        f"/fornecedores/{fornecedor['id']}"
    )

    assert consulta.status_code == 200
    assert consulta.json()["nome"] == "Fornecedor Atualizado"


def test_atualizar_fornecedor_inexistente(cliente):
    resposta = cliente.put(
        "/fornecedores/99999",
        json={
            "nome": "Fornecedor Novo",
            "cnpj": "98765432000198",
            "email": "novo@example.com",
            "telefone": "71988887777",
        },
    )

    assert resposta.status_code == 404


def test_atualizar_fornecedor_com_cnpj_duplicado(cliente):
    criar_fornecedor(cliente)

    segundo = criar_fornecedor(
        cliente,
        cnpj="98765432000198",
        email="segundo@example.com",
        nome="Segundo Fornecedor",
    )

    resposta = cliente.put(
        f"/fornecedores/{segundo['id']}",
        json={
            "nome": "Segundo Fornecedor",
            "cnpj": "12345678000199",
            "email": "segundo@example.com",
            "telefone": "71988887777",
        },
    )

    assert resposta.status_code == 409


def test_excluir_fornecedor(cliente):
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.delete(
        f"/fornecedores/{fornecedor['id']}"
    )

    assert resposta.status_code == 204

    consulta = cliente.get(
        f"/fornecedores/{fornecedor['id']}"
    )

    assert consulta.status_code == 404


def test_excluir_fornecedor_inexistente(cliente):
    resposta = cliente.delete("/fornecedores/99999")

    assert resposta.status_code == 404


def test_excluir_fornecedor_com_produto_associado(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    resposta = cliente.delete(
        f"/fornecedores/{fornecedor['id']}"
    )

    assert resposta.status_code == 409

    # O fornecedor deve continuar existindo.
    consulta = cliente.get(
        f"/fornecedores/{fornecedor['id']}"
    )

    assert consulta.status_code == 200


def test_excluir_categoria_com_produto_associado(cliente):
    # Cria uma categoria.
    categoria = criar_categoria(cliente)

    # Cria um fornecedor para o produto.
    fornecedor = criar_fornecedor(cliente)

    # Cria um produto associado à categoria.
    criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    # Tenta excluir a categoria que possui um produto associado.
    resposta = cliente.delete(
        f"/categorias/{categoria['id']}"
    )

    # A API deve impedir a exclusão.
    assert resposta.status_code == 409

    # Confirma que a categoria continua existindo.
    consulta = cliente.get(
        f"/categorias/{categoria['id']}"
    )

    assert consulta.status_code == 200


def test_atualizar_produto(cliente):
    # Cria as dependências necessárias.
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    # Cria o produto que será atualizado.
    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    # Envia os novos dados do produto.
    resposta = cliente.put(
        f"/produtos/{produto['id']}",
        json={
            "nome": "Mouse Gamer",
            "sku": "MOUSE-GAMER-001",
            "descricao": "Mouse gamer com iluminação RGB",
            "preco_custo": "80.00",
            "preco_venda": "150.00",
            "estoque_minimo": 10,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    # Confirma que a atualização foi bem-sucedida.
    assert resposta.status_code == 200

    dados = resposta.json()

    # Verifica se os dados foram realmente atualizados.
    assert dados["nome"] == "Mouse Gamer"
    assert dados["sku"] == "MOUSE-GAMER-001"
    assert dados["descricao"] == "Mouse gamer com iluminação RGB"
    assert float(dados["preco_custo"]) == 80.00
    assert float(dados["preco_venda"]) == 150.00
    assert dados["estoque_minimo"] == 10

    # Confirma que o estoque inicial não foi alterado.
    assert dados["quantidade_estoque"] == 0


def test_atualizar_produto_inexistente(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.put(
        "/produtos/9999",
        json={
            "nome": "Mouse Gamer",
            "sku": "MOUSE-GAMER-001",
            "descricao": "Mouse gamer",
            "preco_custo": "80.00",
            "preco_venda": "150.00",
            "estoque_minimo": 10,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Produto não encontrado."


def test_atualizar_produto_com_sku_duplicado(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    # Cria dois produtos com SKUs diferentes.
    produto1 = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
        sku="MOUSE-001",
    )

    produto2 = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
        sku="TECLADO-001",
    )

    # Tenta atualizar o segundo produto usando o SKU do primeiro.
    resposta = cliente.put(
        f"/produtos/{produto2['id']}",
        json={
            "nome": "Teclado Mecânico",
            "sku": produto1["sku"],
            "descricao": "Teclado mecânico para teste",
            "preco_custo": "100.00",
            "preco_venda": "200.00",
            "estoque_minimo": 3,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 409
    assert resposta.json()["detail"] == (
        "Já existe outro produto com esse SKU."
    )

    # Confirma que o SKU original do segundo produto foi preservado.
    consulta = cliente.get(f"/produtos/{produto2['id']}")

    assert consulta.status_code == 200
    assert consulta.json()["sku"] == "TECLADO-001"


def test_excluir_produto(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    resposta = cliente.delete(f"/produtos/{produto['id']}")

    assert resposta.status_code == 204

    consulta = cliente.get(f"/produtos/{produto['id']}")

    assert consulta.status_code == 404


def test_excluir_produto_inexistente(cliente):
    resposta = cliente.delete("/produtos/9999")

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Produto não encontrado."


def test_excluir_produto_com_movimentacao_associada(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    # Registra uma entrada para criar uma movimentação associada.
    registrar_movimentacao(
        cliente,
        produto["id"],
        "entrada",
        10,
    )

    # Tenta excluir um produto que possui movimentação registrada.
    resposta = cliente.delete(f"/produtos/{produto['id']}")

    assert resposta.status_code == 409

    assert resposta.json()["detail"] == (
        "Não é possível excluir o produto porque existem movimentações associadas a ele."
    )

    # Confirma que o produto continua existindo.
    consulta = cliente.get(f"/produtos/{produto['id']}")

    assert consulta.status_code == 200


def test_criar_produto_com_nome_vazio(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "",
            "sku": "MOUSE-VAZIO",
            "preco_custo": "30.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_sku_vazio(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "",
            "preco_custo": "30.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_preco_custo_zero(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-CUSTO-ZERO",
            "preco_custo": "0.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_preco_venda_negativo(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-VENDA-NEGATIVO",
            "preco_custo": "30.00",
            "preco_venda": "-10.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_estoque_minimo_negativo(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-ESTOQUE-NEGATIVO",
            "preco_custo": "30.00",
            "preco_venda": "50.00",
            "estoque_minimo": -1,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_categoria_id_zero(cliente):
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-CATEGORIA-ZERO",
            "preco_custo": "30.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": 0,
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_fornecedor_id_negativo(cliente):
    categoria = criar_categoria(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-FORNECEDOR-NEGATIVO",
            "preco_custo": "30.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": -1,
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_campo_nao_permitido(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-CAMPO-EXTRA",
            "preco_custo": "30.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
            "campo_inexistente": "valor",
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_preco_com_mais_de_duas_casas_decimais(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-PRECO-DECIMAL",
            "preco_custo": "30.123",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_criar_produto_com_preco_acima_do_limite(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    resposta = cliente.post(
        "/produtos/",
        json={
            "nome": "Mouse USB",
            "sku": "MOUSE-PRECO-LIMITE",
            "preco_custo": "100000000.00",
            "preco_venda": "50.00",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422


def test_atualizar_produto_com_preco_invalido(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)

    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    resposta = cliente.put(
        f"/produtos/{produto['id']}",
        json={
            "nome": "Mouse USB Atualizado",
            "sku": "MOUSE-PRECO-INVALIDO",
            "descricao": "Teste de preço inválido",
            "preco_custo": "30.00",
            "preco_venda": "50.999",
            "estoque_minimo": 5,
            "categoria_id": categoria["id"],
            "fornecedor_id": fornecedor["id"],
        },
    )

    assert resposta.status_code == 422

    # A atualização inválida não deve alterar o produto.
    consulta = cliente.get(f"/produtos/{produto['id']}")

    assert consulta.status_code == 200
    assert consulta.json()["sku"] == "MOUSE-001"
    assert float(consulta.json()["preco_venda"]) == 50.00


def test_movimentacao_com_produto_inexistente(cliente):
    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": 9999,
            "tipo": "entrada",
            "quantidade": 5,
        },
    )

    assert resposta.status_code == 404
    assert resposta.json()["detail"] == "Produto não encontrado"


def test_movimentacao_com_tipo_invalido(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "transferencia",
            "quantidade": 5,
        },
    )

    assert resposta.status_code == 422


def test_movimentacao_com_produto_id_zero(cliente):
    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": 0,
            "tipo": "entrada",
            "quantidade": 5,
        },
    )

    assert resposta.status_code == 422


def test_movimentacao_com_campo_extra(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 5,
            "campo_inexistente": "valor",
        },
    )

    assert resposta.status_code == 422

    # A requisição inválida não deve alterar o estoque.
    consulta = cliente.get(f"/produtos/{produto['id']}")

    assert consulta.status_code == 200
    assert consulta.json()["quantidade_estoque"] == 0


def test_movimentacao_com_observacao_acima_do_limite(cliente):
    categoria = criar_categoria(cliente)
    fornecedor = criar_fornecedor(cliente)
    produto = criar_produto(
        cliente,
        categoria["id"],
        fornecedor["id"],
    )

    resposta = cliente.post(
        "/movimentacoes-estoque/",
        json={
            "produto_id": produto["id"],
            "tipo": "entrada",
            "quantidade": 5,
            "observacao": "A" * 256,
        },
    )

    assert resposta.status_code == 422

    # Confirma que nenhuma movimentação inválida foi registrada.
    movimentacoes = cliente.get(
        "/movimentacoes-estoque/",
        params={"produto_id": produto["id"]},
    )

    assert movimentacoes.status_code == 200
    assert movimentacoes.json() == []


def test_criar_fornecedor_com_nome_vazio(cliente):
    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": "",
            "cnpj": "12345678000199",
            "email": "fornecedor@example.com",
            "telefone": "71999999999",
        },
    )

    assert resposta.status_code == 422


def test_criar_fornecedor_com_cnpj_com_menos_de_14_digitos(cliente):
    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": "Fornecedor Teste",
            "cnpj": "1234567890123",
            "email": "fornecedor@example.com",
            "telefone": "71999999999",
        },
    )

    assert resposta.status_code == 422


def test_criar_fornecedor_com_email_invalido(cliente):
    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": "Fornecedor Teste",
            "cnpj": "12345678000199",
            "email": "email-invalido",
            "telefone": "71999999999",
        },
    )

    assert resposta.status_code == 422


def test_criar_fornecedor_com_campo_extra(cliente):
    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": "Fornecedor Teste",
            "cnpj": "12345678000199",
            "email": "fornecedor@example.com",
            "telefone": "71999999999",
            "campo_inexistente": "valor",
        },
    )

    assert resposta.status_code == 422


def test_criar_fornecedor_com_cnpj_formatado(cliente):
    resposta = cliente.post(
        "/fornecedores/",
        json={
            "nome": "Fornecedor Formatado",
            "cnpj": "12.345.678/0001-99",
            "email": "formatado@example.com",
            "telefone": "71999999999",
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["cnpj"] == "12345678000199"


def test_criar_categoria_com_nome_vazio(cliente):
    resposta = cliente.post(
        "/categorias/",
        json={
            "nome": "",
            "descricao": "Categoria de teste",
        },
    )

    assert resposta.status_code == 422


def test_criar_categoria_com_nome_acima_do_limite(cliente):
    resposta = cliente.post(
        "/categorias/",
        json={
            "nome": "A" * 101,
            "descricao": "Categoria de teste",
        },
    )

    assert resposta.status_code == 422


def test_criar_categoria_com_descricao_acima_do_limite(cliente):
    resposta = cliente.post(
        "/categorias/",
        json={
            "nome": "Categoria Limite",
            "descricao": "A" * 256,
        },
    )

    assert resposta.status_code == 422


def test_criar_categoria_com_campo_extra(cliente):
    resposta = cliente.post(
        "/categorias/",
        json={
            "nome": "Categoria Extra",
            "descricao": "Categoria de teste",
            "campo_inexistente": "valor",
        },
    )

    assert resposta.status_code == 422


def test_criar_categoria_sem_descricao(cliente):
    resposta = cliente.post(
        "/categorias/",
        json={
            "nome": "Categoria Sem Descricao",
        },
    )

    assert resposta.status_code == 201
    assert resposta.json()["nome"] == "Categoria Sem Descricao"
    assert resposta.json()["descricao"] is None
