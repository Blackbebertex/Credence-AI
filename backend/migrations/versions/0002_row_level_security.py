"""PostgreSQL Row-Level Security (RLS) policies

Revision ID: 0002_row_level_security
Revises: 0001_initial
Create Date: 2026-10-11 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0002_row_level_security"
down_revision: Union[str, None] = "0001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

RLS_TABLES = ["cases", "artifacts", "users"]


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in RLS_TABLES:
            op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
            op.execute(
                f"""
                CREATE POLICY {table}_tenant_isolation_policy
                ON {table}
                FOR ALL
                USING (tenant_id = current_setting('app.current_tenant', true));
                """
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        for table in RLS_TABLES:
            op.execute(f"DROP POLICY IF EXISTS {table}_tenant_isolation_policy ON {table};")
            op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;")
            op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")
