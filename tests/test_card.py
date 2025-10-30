from app.models import User, Card, CardStatus

def test_create_card_for_user(session):
    u = User(email="card@ex.com", full_name="Card User"); session.add(u); session.commit()

    def mask_pan(pan: str) -> str:
        return pan[:6] + "*" * 6 + pan[-4:]

    c = Card(user_id=u.id, masked_pan=mask_pan("5454545454545454"),
             type="virtual", status=CardStatus.active)
    session.add(c); session.commit()

    got = session.query(Card).filter_by(user_id=u.id).one()
    assert got.masked_pan.endswith("5454")
    assert got.status == CardStatus.active
    assert got.user.id == u.id
