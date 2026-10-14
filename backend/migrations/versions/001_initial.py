"""Initial tables.

Revision ID: 001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table("policies", sa.Column("id", sa.Integer(), primary_key=True), sa.Column("max_requests", sa.Integer(), nullable=False), sa.Column("window_seconds", sa.Integer(), nullable=False), sa.Column("failed_login_threshold", sa.Integer(), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False), sa.Column("updated_at", sa.DateTime(), nullable=False))
    op.create_table("security_events", sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True), sa.Column("client_ip", sa.String(45), nullable=False), sa.Column("kind", sa.String(32), nullable=False), sa.Column("endpoint", sa.String(128), nullable=False), sa.Column("status_code", sa.Integer(), nullable=False), sa.Column("detail", sa.String(120), nullable=False), sa.Column("created_at", sa.DateTime(), nullable=False))
    op.create_index("ix_security_events_client_ip", "security_events", ["client_ip"])
    op.create_index("ix_events_ip_time", "security_events", ["client_ip", "created_at"])


def downgrade():
    op.drop_index("ix_events_ip_time", table_name="security_events")
    op.drop_index("ix_security_events_client_ip", table_name="security_events")
    op.drop_table("security_events")
    op.drop_table("policies")
