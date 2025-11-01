import os
from app.db import init_engine_session
from app.models import User, Balance, Card, CardType, CardStatus

# ISO-4217 numeric codes
ISO4217_NUM = {
    "USD": 840,
    "LBP": 422,
}

# Get DB URL (env or local default)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:postgres@localhost:5432/adeptech",
)


def main():
    # Initialize engine + session factory (not via app.__init__)
    engine, SessionLocal = init_engine_session(DATABASE_URL)

    with SessionLocal() as s:
        # Skip if data already present
        if s.query(User).filter_by(email="alice@example.com").first():
            print("⚠️  Seed already present. Skipping.")
            return

        # --- Users ---
        alice = User(full_name="Alice Example", email="alice@example.com")
        bob = User(full_name="Bob Example", email="bob@example.com")
        s.add_all([alice, bob])
        s.flush()  # to get IDs

        # --- Balances ---
        s.add_all([
            Balance(
                user_id=alice.id,
                currency="USD",
                currency_code=ISO4217_NUM["USD"],
                available_minor=100_00,
            ),
            Balance(
                user_id=alice.id,
                currency="LBP",
                currency_code=ISO4217_NUM["LBP"],
                available_minor=2_000_000_00,
            ),
            Balance(
                user_id=bob.id,
                currency="USD",
                currency_code=ISO4217_NUM["USD"],
                available_minor=50_00,
            ),
            Balance(
                user_id=bob.id,
                currency="LBP",
                currency_code=ISO4217_NUM["LBP"],
                available_minor=1_000_000_00,
            ),
        ])

        # --- Card ---
        s.add(
            Card(
                user_id=alice.id,
                masked_pan="545454******5454",
                card_type=CardType.VIRTUAL,
                status=CardStatus.active,
            )
        )

        s.commit()
        print("✅ Database seeded: users alice@example.com, bob@example.com")


if __name__ == "__main__":
    main()
