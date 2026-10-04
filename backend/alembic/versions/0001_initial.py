from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "supervisors",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(120), nullable=False, unique=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "machines",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(40), nullable=False, unique=True),
        sa.Column("name", sa.String(120), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_machines_code", "machines", ["code"])
    op.create_table(
        "shifts",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(8), nullable=False, unique=True),
        sa.Column("name", sa.String(80), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.Column("crosses_midnight", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "stoppage_reasons",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(160), nullable=False, unique=True),
        sa.Column("requires_details", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("details_label", sa.String(120), nullable=True),
        sa.Column("measurement_type", sa.String(32), nullable=False, server_default="duration_minutes"),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("username", sa.String(80), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("role", sa.String(32), nullable=False),
        sa.Column("supervisor_id", sa.Uuid(as_uuid=True), sa.ForeignKey("supervisors.id"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_username", "users", ["username"])
    op.create_table(
        "stoppage_records",
        sa.Column("id", sa.Uuid(as_uuid=True), primary_key=True),
        sa.Column("production_date", sa.Date(), nullable=False),
        sa.Column("shift_id", sa.Uuid(as_uuid=True), sa.ForeignKey("shifts.id"), nullable=False),
        sa.Column("supervisor_id", sa.Uuid(as_uuid=True), sa.ForeignKey("supervisors.id"), nullable=False),
        sa.Column("machine_id", sa.Uuid(as_uuid=True), sa.ForeignKey("machines.id"), nullable=False),
        sa.Column("stoppage_reason_id", sa.Uuid(as_uuid=True), sa.ForeignKey("stoppage_reasons.id"), nullable=False),
        sa.Column("duration_minutes", sa.Numeric(10, 2), nullable=False),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("remarks", sa.Text(), nullable=True),
        sa.Column("created_by", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("updated_by", sa.Uuid(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("duration_minutes > 0", name="ck_stoppage_duration_positive"),
    )
    op.create_index("ix_stoppages_production_date", "stoppage_records", ["production_date"])
    op.create_index("ix_stoppages_shift_id", "stoppage_records", ["shift_id"])
    op.create_index("ix_stoppages_supervisor_id", "stoppage_records", ["supervisor_id"])
    op.create_index("ix_stoppages_machine_id", "stoppage_records", ["machine_id"])
    op.create_index("ix_stoppages_reason_id", "stoppage_records", ["stoppage_reason_id"])
    op.create_index("ix_stoppages_created_at", "stoppage_records", ["created_at"])
    op.create_index("ix_stoppages_date_shift", "stoppage_records", ["production_date", "shift_id"])
    op.create_index("ix_stoppages_date_machine", "stoppage_records", ["production_date", "machine_id"])
    op.create_index("ix_stoppages_deleted_at", "stoppage_records", ["deleted_at"])


def downgrade() -> None:
    op.drop_table("stoppage_records")
    op.drop_table("users")
    op.drop_table("stoppage_reasons")
    op.drop_table("shifts")
    op.drop_index("ix_machines_code", table_name="machines")
    op.drop_table("machines")
    op.drop_table("supervisors")
