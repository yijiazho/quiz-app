"""Add user_id to uploaded_files table

Revision ID: add_user_id_to_uploaded_files
Revises: 08b13ca58ea3
Create Date: 2025-05-20 23:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_user_id_to_uploaded_files'
down_revision: Union[str, None] = '08b13ca58ea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('uploaded_files', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_uploaded_files_user_id',
            'users',
            ['user_id'],
            ['id']
        )


def downgrade() -> None:
    with op.batch_alter_table('uploaded_files', schema=None) as batch_op:
        batch_op.drop_constraint('fk_uploaded_files_user_id', type_='foreignkey')
        batch_op.drop_column('user_id') 