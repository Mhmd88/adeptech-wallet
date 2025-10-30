from sqlalchemy.exc import IntegrityError
from app.models import User, Balance, Transaction, TxnType

CODES = {"USD": 840, "LBP": 422}

def p2p_transfer(session, from_email: str, to_email: str, currency: str, amount_minor: int, idem: str | None = None):
    if currency not in CODES:
        raise ValueError("unsupported currency")
    if amount_minor <= 0:
        raise ValueError("amount must be > 0")

    src = session.query(User).filter_by(email=from_email).first()
    dst = session.query(User).filter_by(email=to_email).first()
    if not src or not dst:
        raise ValueError("from/to user not found")

    sbal = session.query(Balance).filter_by(user_id=src.id, currency=currency).first()
    dbal = session.query(Balance).filter_by(user_id=dst.id, currency=currency).first()
    if not sbal or not dbal:
        raise ValueError("missing balance for one of the users")

    # Prevent overspend
    if sbal.available_minor < amount_minor:
        raise ValueError("insufficient funds")

    # Atomic move
    sbal.available_minor -= amount_minor
    dbal.available_minor += amount_minor

    txn = Transaction(
        from_user_id=src.id,
        to_user_id=dst.id,
        currency=currency,
        currency_code=CODES[currency],
        amount_minor=amount_minor,
        type=TxnType.P2P,
        idempotency_key=idem,
    )
    session.add(txn)

    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise

    return txn
