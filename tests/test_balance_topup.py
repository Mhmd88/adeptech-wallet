from app.models import User, Balance
from app.services.balances import ensure_top_up

def test_top_up_creates_missing_balance_and_increments(session):
    # Arrange: create a user with no balances
    u = User(email="moe@example.com", full_name="Moe", password_hash="x")
    session.add(u); session.commit()

    # Act: top up USD twice
    v1 = ensure_top_up(session, "moe@example.com", "USD", 150)
    v2 = ensure_top_up(session, "moe@example.com", "USD", 50)

    # Assert: balance exists and incremented correctly
    bal = session.query(Balance).filter_by(user_id=u.id, currency="USD").one()
    assert v1 == 150
    assert v2 == 200
    assert bal.available_minor == 200
    assert bal.currency_code == 840
