"""add user_id to users

Revision ID: 23f530a233b2
Revises: add_user_id_to_uploaded_files
Create Date: 2025-05-20 23:45:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23f530a233b2'
down_revision: Union[str, None] = 'add_user_id_to_uploaded_files'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create a new table with the desired schema
    op.create_table(
        'users_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_superuser', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_new_email'), 'users_new', ['email'], unique=True)
    op.create_index(op.f('ix_users_new_id'), 'users_new', ['id'], unique=False)
    op.create_index(op.f('ix_users_new_user_id'), 'users_new', ['user_id'], unique=True)

    # Copy data from the old table to the new one, only copying existing columns
    op.execute('INSERT INTO users_new (id, email, hashed_password, full_name, created_at, updated_at) SELECT id, email, hashed_password, full_name, created_at, updated_at FROM users')

    # Drop the old table
    op.drop_table('users')

    # Rename the new table to the original name
    op.rename_table('users_new', 'users')


def downgrade() -> None:
    """Downgrade schema."""
    # Create a new table without user_id
    op.create_table(
        'users_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_old_email'), 'users_old', ['email'], unique=True)
    op.create_index(op.f('ix_users_old_id'), 'users_old', ['id'], unique=False)

    # Copy data from the new table to the old one
    op.execute('INSERT INTO users_old (id, email, hashed_password, full_name, created_at, updated_at) SELECT id, email, hashed_password, full_name, created_at, updated_at FROM users')

    # Drop the new table
    op.drop_table('users')

    # Rename the old table to the original name
    op.rename_table('users_old', 'users')
