"""init

Revision ID: 4c3d4e7e33d3
Revises: 
Create Date: 2022-07-12 10:34:00.930368

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4c3d4e7e33d3'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('vms',
    sa.Column('created_on', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_on', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
    sa.Column('uuid', sa.String(length=64), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('project_id', sa.String(length=64), nullable=False),
    sa.Column('hypervisor_uuid', sa.String(length=64), nullable=False),
    sa.Column('host', sa.String(length=255), nullable=True),
    sa.Column('cluster', sa.String(length=64), nullable=True),
    sa.Column('hostname', sa.String(length=64), nullable=True),
    sa.Column('ip', sa.String(length=64), nullable=True),
    sa.Column('power_state', sa.String(length=32), nullable=True),
    sa.Column('guest_id', sa.String(length=255), nullable=True),
    sa.Column('guest_full_name', sa.String(length=255), nullable=True),
    sa.Column('tags', sa.PickleType(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('vms')
    # ### end Alembic commands ###
