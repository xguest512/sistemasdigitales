"""estados_sensor table

Revision ID: 03038470652c
Revises: a68a5339c52e
Create Date: 2020-02-29 09:44:23.362581

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03038470652c'
down_revision = 'a68a5339c52e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('estados_sensor',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('sensor_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['sensor_id'], ['sensores.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_estados_sensor_timestamp'), 'estados_sensor', ['timestamp'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_estados_sensor_timestamp'), table_name='estados_sensor')
    op.drop_table('estados_sensor')
    # ### end Alembic commands ###
