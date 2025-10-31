from __future__ import annotations
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash

from app import SessionLocal
from app.models import User, Balance

bp = Blueprint("users", __name__)

CODES = {"USD": 840, "LBP": 422}

@bp.post("")
def create_user():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    full_name = (payload.get("full_name") or "").strip()
    password = payload.get("password") or ""

    if not email or not full_name or not password:
        return jsonify(error="email, full_name, and password are required"), 400

    with SessionLocal() as session:
        # unique email check
        if session.query(User).filter_by(email=email).first():
            return jsonify(error="email already exists"), 409

        u = User(email=email, full_name=full_name, password_hash=generate_password_hash(password))
        session.add(u)
        session.flush()  # get u.id

        # seed USD & LBP balances at 0
        for ccy, code in CODES.items():
            if not session.query(Balance).filter_by(user_id=u.id, currency=ccy).first():
                session.add(Balance(user_id=u.id, currency=ccy, currency_code=code, available_minor=0))

        session.commit()

        # response
        return jsonify({
            "id": u.id,
            "email": u.email,
            "full_name": u.full_name,
            "balances": [{"currency": "USD", "code": 840, "available_minor": 0},
                         {"currency": "LBP", "code": 422, "available_minor": 0}]
        }), 201
