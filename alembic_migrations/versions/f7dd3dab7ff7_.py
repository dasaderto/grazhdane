"""empty message

Revision ID: f7dd3dab7ff7
Revises: f27aca2b0469
Create Date: 2021-11-21 12:27:42.474377

"""
import geoalchemy2
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = 'f7dd3dab7ff7'
down_revision = 'f27aca2b0469'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user_appeals', sa.Column('locate', geoalchemy2.types.Geometry(geometry_type='POINT',
                                                                                 from_text='ST_GeomFromEWKT',
                                                                                 name='geometry'), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user_appeals', 'locate')
    # ### end Alembic commands ###
