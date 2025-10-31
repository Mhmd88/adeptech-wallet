from __future__ import annotations
from flask import Blueprint, request, jsonify

from app import SessionLocal
from app.services.balances import ensure_top_up

bp = Blueprint("balances", __name__)

@bp.post("/topup")
def topup():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    currency = (payload.get("currency") or "").strip().upper()
    amount_minor = payload.get("amount_minor")

    if not email or not currency or not isinstance(amount_minor, int):
        return jsonify(error="email, currency, and integer amount_minor are required"), 400

    with SessionLocal() as session:
        try:
            new_amount = ensure_top_up(session, email, currency, amount_minor)
        except ValueError as e:
            return jsonify(error=str(e)), 400

        return jsonify({
            "email": email,
            "currency": currency,
            "new_available_minor": new_amount
        }), 200
