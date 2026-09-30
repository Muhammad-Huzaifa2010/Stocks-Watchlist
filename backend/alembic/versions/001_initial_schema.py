"""Initial users and stocks schema.

Revision ID: 001_initial
Revises:
Create Date: 2026-09-29

This migration is additive and data-preserving:
- Creates missing tables on a fresh database.
- Aligns column lengths on existing databases when values already fit.
- Adds UNIQUE (user_id, symbol) only when no duplicate owned stocks exist.
- Does not DROP, TRUNCATE, or DELETE rows.
- Does not force stocks.user_id NOT NULL while ownerless rows exist.
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect, text


revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _index_names(inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def _unique_names(inspector, table_name: str) -> set[str]:
    names = {item["name"] for item in inspector.get_unique_constraints(table_name)}
    names.update(
        index["name"]
        for index in inspector.get_indexes(table_name)
        if index.get("unique")
    )
    return {name for name in names if name}


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = set(inspector.get_table_names())
    dialect = bind.dialect.name

    if "users" not in tables:
        op.create_table(
            "users",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("username", sa.String(length=30), nullable=False),
            sa.Column("email", sa.String(length=254), nullable=False),
            sa.Column("hashed_password", sa.String(length=255), nullable=False),
        )
        op.create_index("ix_users_username", "users", ["username"], unique=True)
        op.create_index("ix_users_email", "users", ["email"], unique=True)
    elif dialect == "postgresql":
        op.execute("ALTER TABLE users ALTER COLUMN username TYPE VARCHAR(30)")
        op.execute("ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(254)")
        op.execute(
            "ALTER TABLE users ALTER COLUMN hashed_password TYPE VARCHAR(255)"
        )
        if "ix_users_id" in _index_names(inspector, "users"):
            op.drop_index("ix_users_id", table_name="users")

    inspector = inspect(bind)
    tables = set(inspector.get_table_names())

    if "stocks" not in tables:
        op.create_table(
            "stocks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("symbol", sa.String(length=10), nullable=False),
            sa.Column("company_name", sa.String(length=100), nullable=False),
            sa.Column("market", sa.String(length=50), nullable=False),
            sa.Column("sector", sa.String(length=100), nullable=True),
            sa.Column("notes", sa.String(length=500), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.UniqueConstraint(
                "user_id",
                "symbol",
                name="uq_stocks_user_id_symbol",
            ),
        )
        op.create_index("ix_stocks_user_id", "stocks", ["user_id"])
        return

    duplicate_owned = bind.execute(
        text(
            """
            SELECT COUNT(*) FROM (
                SELECT user_id, UPPER(symbol)
                FROM stocks
                WHERE user_id IS NOT NULL
                GROUP BY user_id, UPPER(symbol)
                HAVING COUNT(*) > 1
            ) duplicates
            """
        )
    ).scalar_one()

    if duplicate_owned:
        raise RuntimeError(
            "Refusing to add UNIQUE (user_id, symbol) because duplicate owned "
            "stocks already exist. Resolve duplicates manually, then rerun "
            "alembic upgrade head."
        )

    inspector = inspect(bind)
    if "uq_stocks_user_id_symbol" not in _unique_names(inspector, "stocks"):
        op.create_unique_constraint(
            "uq_stocks_user_id_symbol",
            "stocks",
            ["user_id", "symbol"],
        )


def downgrade() -> None:
    raise RuntimeError("Downgrade is disabled to protect existing data.")
