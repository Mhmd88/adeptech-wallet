from flask import Blueprint, request, jsonify
from app import SessionLocal
from app.services.users import create_user

bp = Blueprint("users", __name__)

@bp.post("/")
def create_user_route():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    full_name = (data.get("full_name") or "").strip()
    password = data.get("password") or ""

    with SessionLocal() as session:
        try:
            user = create_user(session, email, full_name, password)
        except ValueError as e:
            return jsonify(error=str(e)), 400

        return jsonify({
            "id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "balances": [
                {"currency": "USD", "code": 840, "available_minor": 0},
                {"currency": "LBP", "code": 422, "available_minor": 0}
            ]
        }), 201
