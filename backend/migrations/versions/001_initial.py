"""Initial migration

Revision ID: 001
Create Date: 2025-06-18 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(80), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(128), nullable=False),
        sa.Column('role', sa.String(20), nullable=False),
        sa.Column('email', sa.String(120), unique=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('last_login', sa.DateTime()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_username', 'users', ['username'])
    op.create_index('idx_user_email', 'users', ['email'])
    op.create_index('idx_user_role', 'users', ['role'])

    # Create vendors table
    op.create_table(
        'vendors',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(120), unique=True, nullable=False),
        sa.Column('average_rate', sa.Float()),
        sa.Column('diversity_score', sa.Float()),
        sa.Column('success_rate', sa.Float()),
        sa.Column('total_invoices', sa.Integer()),
        sa.Column('total_spend', sa.Float()),
        sa.Column('cluster', sa.Integer()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_vendor_name', 'vendors', ['name'])
    op.create_index('idx_vendor_cluster', 'vendors', ['cluster'])

    # Create invoices table
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(64)),
        sa.Column('vendor_id', sa.Integer(), nullable=False),
        sa.Column('matter_id', sa.Integer()),
        sa.Column('amount', sa.Float()),
        sa.Column('date', sa.Date()),
        sa.Column('status', sa.String(20), default='pending'),
        sa.Column('description', sa.Text()),
        sa.Column('hours', sa.Float()),
        sa.Column('rate', sa.Float()),
        sa.Column('risk_score', sa.Float()),
        sa.Column('analysis_result', sa.JSON()),
        sa.Column('pdf_s3_key', sa.String(256)),
        sa.Column('overspend_risk', sa.Float()),
        sa.Column('uploaded_by', sa.Integer()),
        sa.Column('uploaded_at', sa.DateTime()),
        sa.Column('processed', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['vendor_id'], ['vendors.id']),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_invoice_date', 'invoices', ['date'])
    op.create_index('idx_invoice_vendor', 'invoices', ['vendor_id'])
    op.create_index('idx_invoice_status', 'invoices', ['status'])

def downgrade():
    op.drop_table('invoices')
    op.drop_table('vendors')
    op.drop_table('users')
