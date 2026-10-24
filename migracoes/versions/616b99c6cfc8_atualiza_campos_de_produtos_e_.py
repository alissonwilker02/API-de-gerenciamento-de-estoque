
"""Atualiza campos de produtos e fornecedores.

Revision ID: 616b99c6cfc8
Revises: 42dac2d2274f
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Identificadores da migration.
revision: str = "616b99c6cfc8"
down_revision: Union[str, Sequence[str], None] = "42dac2d2274f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Atualiza as tabelas de fornecedores e produtos."""

    # Adiciona o CNPJ obrigatório e exclusivo dos fornecedores.
    op.add_column(
        "fornecedores",
        sa.Column("cnpj", sa.String(length=18), nullable=False),
    )
    op.create_index(
        op.f("ix_fornecedores_cnpj"),
        "fornecedores",
        ["cnpj"],
        unique=True,
    )

    # Adiciona os novos campos dos produtos.
    op.add_column(
        "produtos",
        sa.Column("sku", sa.String(length=50), nullable=False),
    )
    op.add_column(
        "produtos",
        sa.Column(
            "preco_custo",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
    )
    op.add_column(
        "produtos",
        sa.Column(
            "preco_venda",
            sa.Numeric(precision=10, scale=2),
            nullable=False,
        ),
    )
    op.add_column(
        "produtos",
        sa.Column(
            "data_cadastro",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )

    op.create_index(
        op.f("ix_produtos_sku"),
        "produtos",
        ["sku"],
        unique=True,
    )

    # Remove a coluna de preço antiga, substituída pelos dois novos campos.
    op.drop_column("produtos", "preco")


def downgrade() -> None:
    """Reverte as alterações desta migration."""

    # Restaura a coluna antiga antes de remover os novos preços.
    op.add_column(
        "produtos",
        sa.Column(
            "preco",
            sa.Numeric(precision=10, scale=2),
            nullable=True,
        ),
    )

    op.drop_index(op.f("ix_produtos_sku"), table_name="produtos")
    op.drop_column("produtos", "data_cadastro")
    op.drop_column("produtos", "preco_venda")
    op.drop_column("produtos", "preco_custo")
    op.drop_column("produtos", "sku")

    op.drop_index(op.f("ix_fornecedores_cnpj"), table_name="fornecedores")
    op.drop_column("fornecedores", "cnpj")
