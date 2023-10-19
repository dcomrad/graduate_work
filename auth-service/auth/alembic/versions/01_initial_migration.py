"""Initial migration

Revision ID: 6dba2e92fe2b
Revises:
Create Date: 2023-06-14 22:21:00.994745

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '6dba2e92fe2b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("CREATE SCHEMA IF NOT EXISTS users;")
    op.create_table('permission',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='users'
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name'),
    schema='users'
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('login', sa.String(length=100), nullable=False),
    sa.Column('hashed_password', sa.Text(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=False),
    sa.Column('full_name', sa.String(length=100), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('login'),
    schema='users'
    )
    op.create_table('access_history',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('access_time', sa.DateTime(timezone=True), nullable=False),
    sa.Column('user_agent', sa.String(length=200), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['users.user.id'], ),
    sa.PrimaryKeyConstraint('id', 'access_time'),
    sa.UniqueConstraint('id', 'access_time'),
    schema='users',
    postgresql_partition_by='RANGE (access_time)'
    )
    op.create_table('role_permission',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['users.permission.id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['users.role.id'], ),
    sa.PrimaryKeyConstraint('role_id', 'permission_id'),
    schema='users'
    )
    op.create_table('user_role',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['users.role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user.id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id'),
    schema='users'
    )
    op.execute(
    """CREATE TABLE IF NOT EXISTS access_history_2023 PARTITION OF users.access_history FOR VALUES FROM ('01.01.2023') TO ('01.01.2024')"""
    )
    op.execute(
    """CREATE TABLE IF NOT EXISTS access_history_2024 PARTITION OF users.access_history FOR VALUES FROM ('01.01.2024') TO ('01.01.2025')"""
    )
    op.execute(
    """CREATE TABLE IF NOT EXISTS access_history_2025 PARTITION OF users.access_history FOR VALUES FROM ('01.01.2025') TO ('01.01.2026')"""
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("""DROP TABLE IF EXISTS access_history_2023""")
    op.execute("""DROP TABLE IF EXISTS access_history_2024""")
    op.execute("""DROP TABLE IF EXISTS access_history_2025""")
    op.drop_table('user_role', schema='users')
    op.drop_table('role_permission', schema='users')
    op.drop_table('access_history', schema='users')
    op.drop_table('user', schema='users')
    op.drop_table('role', schema='users')
    op.drop_table('permission', schema='users')
    # ### end Alembic commands ###
