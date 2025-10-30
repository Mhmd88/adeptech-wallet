from app.models import User, Balance
from app.services.transfers import p2p_transfer

def test_p2p_same_currency_and_no_overspend(session):
    a = User(email="a@ex.com", full_name="A"); b = User(email="b@ex.com", full_name="B")
    session.add_all([a, b]); session.commit()

    # Seed balances (USD)
    sa = Balance(user_id=a.id, currency="USD", currency_code=840, available_minor=500)
    sb = Balance(user_id=b.id, currency="USD", currency_code=840, available_minor=100)
    session.add_all([sa, sb]); session.commit()

    txn = p2p_transfer(session, "a@ex.com", "b@ex.com", "USD", 200)
    session.refresh(sa); session.refresh(sb)

    assert sa.available_minor == 300
    assert sb.available_minor == 300
    assert txn.amount_minor == 200
    assert txn.currency == "USD"
