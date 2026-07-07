"""initial schema

Revision ID: 3f1c9d2a7b44
Revises:
Create Date: 2026-07-07 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "3f1c9d2a7b44"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organization",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.UniqueConstraint("code", name="uq_organization_code"),
    )

    op.create_table(
        "unit",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=64), nullable=False),
    )

    op.create_table(
        "category",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "movement_type",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.UniqueConstraint("code", name="uq_movement_type_code"),
    )

    op.create_table(
        "warehouse",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organization.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.UniqueConstraint("organization_id", "name", name="uq_warehouse_org_name"),
    )

    op.create_table(
        "location",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouse.id"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("location.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "material",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("article", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("unit_id", sa.Integer(), sa.ForeignKey("unit.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("category.id"), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.UniqueConstraint("article", name="uq_material_article"),
    )

    op.create_table(
        "employee",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("last_name", sa.String(length=128), nullable=False),
        sa.Column("first_name", sa.String(length=128), nullable=False),
        sa.Column("middle_name", sa.String(length=128), nullable=True),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organization.id"), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "material_movement",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("material_id", sa.Integer(), sa.ForeignKey("material.id"), nullable=False),
        sa.Column("warehouse_id", sa.Integer(), sa.ForeignKey("warehouse.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("location.id"), nullable=False),
        sa.Column("movement_type_id", sa.Integer(), sa.ForeignKey("movement_type.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("operation_date", sa.DateTime(timezone=True), nullable=False),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employee.id"), nullable=False),
        sa.Column("unit_price", sa.Numeric(18, 4), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("document_ref", sa.String(length=255), nullable=True),
        sa.CheckConstraint("quantity > 0", name="ck_material_movement_quantity_positive"),
    )

    op.create_table(
        "stock_balance",
        sa.Column("material_id", sa.Integer(), sa.ForeignKey("material.id"), primary_key=True),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("location.id"), primary_key=True),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("last_updated", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("quantity >= 0", name="ck_stock_balance_quantity_non_negative"),
    )

    op.create_table(
        "reservation",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("material_id", sa.Integer(), sa.ForeignKey("material.id"), nullable=False),
        sa.Column("location_id", sa.Integer(), sa.ForeignKey("location.id"), nullable=False),
        sa.Column("quantity", sa.Numeric(18, 4), nullable=False),
        sa.Column("employee_id", sa.Integer(), sa.ForeignKey("employee.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.CheckConstraint("quantity > 0", name="ck_reservation_quantity_positive"),
    )

    op.create_table(
        "outbox_event",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("aggregate_type", sa.String(length=64), nullable=False),
        sa.Column("aggregate_id", sa.Integer(), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("payload", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("outbox_event")
    op.drop_table("reservation")
    op.drop_table("stock_balance")
    op.drop_table("material_movement")
    op.drop_table("employee")
    op.drop_table("material")
    op.drop_table("location")
    op.drop_table("warehouse")
    op.drop_table("movement_type")
    op.drop_table("category")
    op.drop_table("unit")
    op.drop_table("organization")
