"""many-to-many artists, label <-> release

Revision ID: 855cba5c0cc5
Revises: 171a08973553
Create Date: 2023-12-27 12:26:21.905060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '855cba5c0cc5'
down_revision = '171a08973553'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist_release',
    sa.Column('artist_id', sa.UUID(), nullable=False),
    sa.Column('release_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artist.id'], ),
    sa.ForeignKeyConstraint(['release_id'], ['release.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'release_id')
    )
    op.create_table('label_release',
    sa.Column('label_id', sa.UUID(), nullable=False),
    sa.Column('release_id', sa.UUID(), nullable=False),
    sa.ForeignKeyConstraint(['label_id'], ['label.id'], ),
    sa.ForeignKeyConstraint(['release_id'], ['release.id'], ),
    sa.PrimaryKeyConstraint('label_id', 'release_id')
    )
    op.drop_constraint('artist_release_id_fkey', 'artist', type_='foreignkey')
    op.drop_column('artist', 'release_id')
    op.drop_constraint('label_release_id_fkey', 'label', type_='foreignkey')
    op.drop_column('label', 'release_id')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('label', sa.Column('release_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('label_release_id_fkey', 'label', 'release', ['release_id'], ['id'])
    op.add_column('artist', sa.Column('release_id', sa.UUID(), autoincrement=False, nullable=True))
    op.create_foreign_key('artist_release_id_fkey', 'artist', 'release', ['release_id'], ['id'])
    op.drop_table('label_release')
    op.drop_table('artist_release')
    # ### end Alembic commands ###
