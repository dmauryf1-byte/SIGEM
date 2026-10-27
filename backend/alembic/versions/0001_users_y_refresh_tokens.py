"""users y refresh_tokens (SIGEM-004)

Revision ID: 0001
Revises:
Create Date: 2026-10-27

Revisada a mano. La colación utf8mb4_0900_ai_ci hace que username sea único sin distinguir
mayúsculas ni tildes ("Ana" y "ana" son el mismo usuario).
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.Column("full_name", sa.String(length=120), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.Enum("Administrador", "Vendedor", name="user_role"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.Column("failed_login_attempts", sa.Integer(), server_default="0", nullable=False),
        sa.Column("locked_until", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.String(length=43), nullable=False),
        sa.Column("token_hash", sa.CHAR(length=64), nullable=False),
        sa.Column("session_started_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token_hash"),
    )
    op.create_index("ix_refresh_tokens_session_id", "refresh_tokens", ["session_id"])
    op.create_index("ix_refresh_tokens_user_id", "refresh_tokens", ["user_id"])


def downgrade() -> None:
    op.drop_table("refresh_tokens")
    op.drop_table("users")
