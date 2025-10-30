from app.models import User, Balance

CURRENCY_CODES = {"USD": 840, "LBP": 422}

def ensure_top_up(session, email: str, currency: str, amount_minor: int) -> int:
    """Create balance if missing and increment; return new available_minor."""
    if amount_minor <= 0:
        raise ValueError("amount_minor must be > 0")
    if currency not in CURRENCY_CODES:
        raise ValueError("unsupported currency")

    user = session.query(User).filter_by(email=email).first()
    if not user:
        raise ValueError(f"User with email {email} not found")

    bal = session.query(Balance).filter_by(user_id=user.id, currency=currency).first()
    if not bal:
        bal = Balance(
            user_id=user.id,
            currency=currency,
            currency_code=CURRENCY_CODES[currency],
            available_minor=0,
        )
        session.add(bal)
        session.flush()

    bal.available_minor += amount_minor
    session.commit()
    return bal.available_minor
