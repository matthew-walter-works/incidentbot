"""Add upstream_id column to StatuspageIncidentRecord

Revision ID: e8a0a978b5f7
Revises: c084a30ce811
Create Date: 2024-10-05 12:05:52.049512

"""

from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e8a0a978b5f7"
down_revision = "c084a30ce811"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "statuspageincidentrecord",
        sa.Column(
            "upstream_id", sqlmodel.sql.sqltypes.AutoString(), nullable=False
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("statuspageincidentrecord", "upstream_id")
    # ### end Alembic commands ###