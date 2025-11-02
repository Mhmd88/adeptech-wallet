from werkzeug.security import generate_password_hash
from app.models import User, Balance

CODES = {"USD": 840, "LBP": 422}

def create_user(session, email: str, full_name: str, password: str):
    if not email or not full_name or not password:
        raise ValueError("email, full_name, and password are required")

    if session.query(User).filter_by(email=email).first():
        raise ValueError("email already exists")

    user = User(email=email, full_name=full_name, password_hash=generate_password_hash(password))
    session.add(user)
    session.flush()  # get user.id

    for ccy, code in CODES.items():
        if not session.query(Balance).filter_by(user_id=user.id, currency=ccy).first():
            session.add(Balance(user_id=user.id, currency=ccy, currency_code=code, available_minor=0))

    session.commit()
    return user
