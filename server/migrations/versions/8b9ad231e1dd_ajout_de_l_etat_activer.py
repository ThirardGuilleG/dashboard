"""Ajout de l'etat activer

Revision ID: 8b9ad231e1dd
Revises: 
Create Date: 2021-07-28 11:15:13.395102

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b9ad231e1dd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('server', sa.Column('active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('server', 'active')
    # ### end Alembic commands ###
