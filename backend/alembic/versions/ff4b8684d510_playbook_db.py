"""Playbook DB

Revision ID: ff4b8684d510
Revises: 
Create Date: 2023-11-29 17:48:21.618415

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ff4b8684d510'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('playbook_db',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('project_name', sa.String(), nullable=True),
    sa.Column('date_year', sa.Integer(), nullable=True),
    sa.Column('number_of_wtgs', sa.Integer(), nullable=True),
    sa.Column('oem', sa.String(), nullable=True),
    sa.Column('wtg_capacity_mw', sa.Float(), nullable=True),
    sa.Column('region', sa.String(), nullable=True),
    sa.Column('foundation_type', sa.String(), nullable=True),
    sa.Column('number_of_substations', sa.Integer(), nullable=True),
    sa.Column('distance_from_port_km', sa.Float(), nullable=True),
    sa.Column('lifetime_years', sa.Integer(), nullable=True),
    sa.Column('annual_cost_per_wtg_eur', sa.Float(), nullable=True),
    sa.Column('annual_cost_per_mw_eur', sa.Float(), nullable=True),
    sa.Column('tba_percent', sa.Float(), nullable=True),
    sa.Column('pba_percent', sa.Float(), nullable=True),
    sa.Column('project_development_stage', sa.String(), nullable=True),
    sa.Column('weight', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_playbook_db_id'), 'playbook_db', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_playbook_db_id'), table_name='playbook_db')
    op.drop_table('playbook_db')
    # ### end Alembic commands ###