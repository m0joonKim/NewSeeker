"""add sunday

Revision ID: 5f16a73d32de
Revises: b92626cb8663
Create Date: 2025-05-15 18:41:02.708808

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel.sql.sqltypes


# revision identifiers, used by Alembic.
revision = '5f16a73d32de'
down_revision = 'b92626cb8663'
branch_labels = None
depends_on = None


def upgrade():
    # Add 'SUNDAY' to the DayOfWeekEnum type
    op.execute("ALTER TYPE dayofweekenum ADD VALUE 'SUNDAY'")


def downgrade():
    # Downgrade logic is not straightforward for enum types in PostgreSQL
    # You might need to recreate the enum type without 'sunday' if necessary
    pass