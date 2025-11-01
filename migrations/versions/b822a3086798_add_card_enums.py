from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "b822a3086798"
down_revision = "ed300b0393ac"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # Create enum types (idempotent)
    cardtype_enum = postgresql.ENUM("PHYSICAL", "VIRTUAL", name="cardtype", create_type=False)
    cardstatus_enum = postgresql.ENUM("active", "frozen", "cancelled", name="cardstatus", create_type=False)
    cardtype_enum.create(bind, checkfirst=True)
    cardstatus_enum.create(bind, checkfirst=True)

    # Introspect existing columns
    cols = {c["name"]: c for c in insp.get_columns("cards")}

    # --- card_type ---
    if "card_type" not in cols:
        op.add_column("cards", sa.Column("card_type", cardtype_enum, nullable=True))
        op.execute("UPDATE cards SET card_type = 'VIRTUAL' WHERE card_type IS NULL;")
        op.alter_column("cards", "card_type", nullable=False)
    else:
        # If existing type isn't enum, convert to enum
        if not isinstance(cols["card_type"]["type"], postgresql.ENUM):
            op.alter_column(
                "cards",
                "card_type",
                type_=cardtype_enum,
                postgresql_using="card_type::text::cardtype",
            )

    # --- status ---
    if "status" not in cols:
        op.add_column("cards", sa.Column("status", cardstatus_enum, nullable=True))
        op.execute("UPDATE cards SET status = 'active' WHERE status IS NULL;")
        op.alter_column("cards", "status", nullable=False)
    else:
        if not isinstance(cols["status"]["type"], postgresql.ENUM):
            op.alter_column(
                "cards",
                "status",
                type_=cardstatus_enum,
                postgresql_using="status::text::cardstatus",
            )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    cardtype_enum = postgresql.ENUM("PHYSICAL", "VIRTUAL", name="cardtype", create_type=False)
    cardstatus_enum = postgresql.ENUM("active", "frozen", "cancelled", name="cardstatus", create_type=False)

    cols = {c["name"]: c for c in insp.get_columns("cards")}

    # Convert back to TEXT (so we can drop the enum types safely)
    if "status" in cols and isinstance(cols["status"]["type"], postgresql.ENUM):
        op.alter_column("cards", "status", type_=sa.String())

    if "card_type" in cols and isinstance(cols["card_type"]["type"], postgresql.ENUM):
        op.alter_column("cards", "card_type", type_=sa.String())

    # Drop enum types (idempotent)
    cardstatus_enum.drop(bind, checkfirst=True)
    cardtype_enum.drop(bind, checkfirst=True)
