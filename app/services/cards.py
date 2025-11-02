from app.models import Card, User, CardType, CardStatus

class CardError(Exception): ...
class CardAlreadyExists(CardError): ...
class UserNotFound(CardError): ...

def create_card(session, email: str, masked_pan: str, card_type: str, status: str):
    email = (email or "").strip().lower()
    masked_pan = (masked_pan or "").strip()
    if not email or not masked_pan:
        raise CardError("email and masked_pan are required")

    user = session.query(User).filter_by(email=email).first()
    if not user:
        raise UserNotFound(f"user {email} not found")

    if session.query(Card).filter_by(masked_pan=masked_pan).first():
        raise CardAlreadyExists("card with this PAN already exists")

    type_enum = getattr(CardType, (card_type or "PHYSICAL").upper(), CardType.PHYSICAL)
    status_enum = getattr(CardStatus, (status or "active").lower(), CardStatus.active)

    card = Card(
        user_id=user.id,
        masked_pan=masked_pan,
        card_type=type_enum,    
        status=status_enum
    )
    session.add(card)
    session.commit()
    return card
