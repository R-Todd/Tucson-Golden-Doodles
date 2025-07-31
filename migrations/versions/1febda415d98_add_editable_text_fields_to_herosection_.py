"""Add editable text fields to HeroSection model and migrate data

Revision ID: 1febda415d98
Revises: 0f0e1671ce93
Create Date: 2025-07-30 15:48:31.428384

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '1febda415d98'
down_revision = '0f0e1671ce93'
branch_labels = None
depends_on = None


def upgrade():
    # ### Part 1: Add the new columns we need ###
    with op.batch_alter_table('hero_section', schema=None) as batch_op:
        batch_op.add_column(sa.Column('main_title', sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column('description', sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column('scroll_text_main', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('scroll_text_secondary', sa.String(length=100), nullable=True))

    # ### Part 2: Manually migrate data from the old 'title' column to 'main_title' ###
    # This raw SQL command copies your existing hero title to the new field.
    print("Migrating data from 'title' to 'main_title'...")
    op.execute("UPDATE hero_section SET main_title = title")
    print("Data migration complete.")

    # ### Part 3: Now that data is safe, drop the old columns ###
    with op.batch_alter_table('hero_section', schema=None) as batch_op:
        batch_op.drop_column('cta_link')
        batch_op.drop_column('title')
        batch_op.drop_column('cta_text')
        # Also alter the 'subtitle' column which is being repurposed
        batch_op.alter_column('subtitle',
               existing_type=mysql.VARCHAR(length=300),
               type_=sa.String(length=200),
               existing_nullable=True)


def downgrade():
    # ### To reverse the process, we first add the old columns back ###
    with op.batch_alter_table('hero_section', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cta_text', mysql.VARCHAR(length=50), nullable=True))
        batch_op.add_column(sa.Column('title', mysql.VARCHAR(length=200), nullable=True))
        batch_op.add_column(sa.Column('cta_link', mysql.VARCHAR(length=255), nullable=True))
        batch_op.alter_column('subtitle',
               existing_type=sa.String(length=200),
               type_=mysql.VARCHAR(length=300),
               existing_nullable=True)

    # ### Then, we copy the data back ###
    op.execute('UPDATE hero_section SET title = main_title')

    # ### Finally, we drop the new columns ###
    with op.batch_alter_table('hero_section', schema=None) as batch_op:
        batch_op.drop_column('scroll_text_secondary')
        batch_op.drop_column('scroll_text_main')
        batch_op.drop_column('description')
        batch_op.drop_column('main_title')