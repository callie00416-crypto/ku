"""
Migration to add missing extra_metadata column to devices table
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_extra_metadata_to_devices'
down_revision = '001_initial_schema'
branch_labels = None
depends_on = None


def upgrade():
    """Add extra_metadata column to devices table"""
    # Add the extra_metadata column to devices table
    op.add_column('devices', sa.Column('extra_metadata', sa.JSON(), nullable=True))
    
    # Also add indexes that might be missing
    with op.get_context().autocommit_block():
        op.create_index(op.f('ix_devices_extra_metadata'), 'devices', ['extra_metadata'], unique=False)


def downgrade():
    """Remove extra_metadata column from devices table"""
    op.drop_index(op.f('ix_devices_extra_metadata'), table_name='devices')
    op.drop_column('devices', 'extra_metadata')