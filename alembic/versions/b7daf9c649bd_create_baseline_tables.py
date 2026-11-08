"""create_baseline_tables

Revision ID: b7daf9c649bd
Revises: b0a272086cd8
Create Date: 2026-11-07 18:01:28.289431

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "b7daf9c649bd"
down_revision: Union[str, Sequence[str], None] = "b0a272086cd8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
