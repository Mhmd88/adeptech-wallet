"""drop legacy cards.type column

Revision ID: 706f20371235
Revises: b822a3086798
Create Date: 2025-11-02 00:20:40.251046

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "706f20371235"
down_revision = "b822a3086798"  # your last revision that added enums
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)

    # get current columns on cards
    cols = {c["name"]: c for c in insp.get_columns("cards")}

    # If legacy 'type' column exists, optionally backfill and drop it
    if "type" in cols:
        # If card_type exists, backfill it from legacy 'type' values (PHYSICAL/VIRTUAL).
        op.execute("""
            DO $$
            BEGIN
                IF EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name='cards' AND column_name='card_type'
                ) THEN
                    UPDATE cards
                    SET card_type = CASE
                        WHEN LOWER(type) = 'physical' THEN 'PHYSICAL'::cardtype
                        WHEN LOWER(type) = 'virtual'  THEN 'VIRTUAL'::cardtype
                        ELSE card_type
                    END
                    WHERE card_type IS NULL AND type IS NOT NULL;
                END IF;
            END $$;
        """)

        # Drop the legacy column
        op.drop_column("cards", "type")


def downgrade() -> None:
    # Recreate legacy column as nullable TEXT (can’t safely restore enum values)
    op.add_column("cards", sa.Column("type", sa.String(), nullable=True))
