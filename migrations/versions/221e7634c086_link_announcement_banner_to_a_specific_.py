"""Link announcement banner to a specific litter

Revision ID: 221e7634c086
Revises: 3d1c2d436dc1
Create Date: 2025-07-30 16:51:08.630928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '221e7634c086'
down_revision = '3d1c2d436dc1'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('announcement_banner', schema=None) as batch_op:
        batch_op.add_column(sa.Column('featured_puppy_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(None, 'puppy', ['featured_puppy_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('announcement_banner', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('featured_puppy_id')

    # ### end Alembic commands ###
