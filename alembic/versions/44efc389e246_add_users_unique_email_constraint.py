"""Add users unique email constraint

Revision ID: 44efc389e246
Revises: 8d60f8474f92
Create Date: 2026-07-03 18:12:35.444798

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '44efc389e246'
down_revision: Union[str, Sequence[str], None] = '8d60f8474f92'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint("uq_email", "users", ["email"])
    pass


def downgrade() -> None:
    op.drop_constraint("uq_email", "users")
    pass
