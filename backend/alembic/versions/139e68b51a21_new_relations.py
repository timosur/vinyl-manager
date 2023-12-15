"""new relations

Revision ID: 139e68b51a21
Revises: a0ab444e5cb6
Create Date: 2023-12-14 14:04:11.567238

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '139e68b51a21'
down_revision = 'a0ab444e5cb6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('release_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'artist', 'release', ['release_id'], ['id'])
    op.add_column('label', sa.Column('release_id', sa.UUID(), nullable=True))
    op.create_foreign_key(None, 'label', 'release', ['release_id'], ['id'])
    op.drop_constraint('release_artist_id_fkey', 'release', type_='foreignkey')
    op.drop_constraint('release_label_id_fkey', 'release', type_='foreignkey')
    op.drop_column('release', 'label_id')
    op.drop_column('release', 'artist_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('release', sa.Column('artist_id', sa.UUID(), autoincrement=False, nullable=True))
    op.add_column('release', sa.Column('label_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('release_label_id_fkey', 'release', 'label', ['label_id'], ['id'])
    op.create_foreign_key('release_artist_id_fkey', 'release', 'artist', ['artist_id'], ['id'])
    op.drop_constraint(None, 'label', type_='foreignkey')
    op.drop_column('label', 'release_id')
    op.drop_constraint(None, 'artist', type_='foreignkey')
    op.drop_column('artist', 'release_id')
    # ### end Alembic commands ###