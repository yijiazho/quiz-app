"""Update file model to use file_id as primary key

Revision ID: 005
Revises: 004
Create Date: 2024-05-26 21:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create a temporary table with the new schema
    op.create_table(
        'uploaded_files_new',
        sa.Column('file_id', sa.String(), nullable=False),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_content', sa.LargeBinary(), nullable=False),
        sa.Column('upload_time', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('file_id')
    )
    
    # Copy data from old table to new table
    op.execute("""
        INSERT INTO uploaded_files_new (
            file_id, filename, content_type, file_size, file_content,
            upload_time, last_accessed, title, description, user_id
        )
        SELECT 
            file_id, filename, content_type, file_size, file_content,
            upload_time, last_accessed, title, description, user_id
        FROM uploaded_files
    """)
    
    # Drop the old table
    op.drop_table('uploaded_files')
    
    # Rename the new table to the original name
    op.rename_table('uploaded_files_new', 'uploaded_files')


def downgrade() -> None:
    # Create a temporary table with the old schema
    op.create_table(
        'uploaded_files_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.String(), nullable=True),
        sa.Column('filename', sa.String(), nullable=False),
        sa.Column('content_type', sa.String(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_content', sa.LargeBinary(), nullable=False),
        sa.Column('upload_time', sa.DateTime(), nullable=True),
        sa.Column('last_accessed', sa.DateTime(), nullable=True),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data from new table to old table
    op.execute("""
        INSERT INTO uploaded_files_old (
            file_id, filename, content_type, file_size, file_content,
            upload_time, last_accessed, title, description, user_id
        )
        SELECT 
            file_id, filename, content_type, file_size, file_content,
            upload_time, last_accessed, title, description, user_id
        FROM uploaded_files
    """)
    
    # Drop the new table
    op.drop_table('uploaded_files')
    
    # Rename the old table to the original name
    op.rename_table('uploaded_files_old', 'uploaded_files') 