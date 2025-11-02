# app/routes/cards.py
from flask import Blueprint, request, jsonify
from app import SessionLocal
from app.services.cards import create_card, CardError, CardAlreadyExists

bp = Blueprint("cards", __name__)

@bp.post("/")
def create_card_route():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    masked_pan = (payload.get("masked_pan") or "").strip()
    card_type = (payload.get("type") or "PHYSICAL").upper()
    status = (payload.get("status") or "active").lower()

    if not email or not masked_pan:
        return jsonify(error="email and masked_pan are required"), 400

    with SessionLocal() as session:
        try:
            card = create_card(session, email, masked_pan, card_type, status)  
        except CardAlreadyExists:
            return jsonify(error="card with this PAN already exists"), 409
        except CardError as e:
            return jsonify(error=str(e)), 400

        return jsonify({
            "id": str(card.id),
            "user_id": str(card.user_id),
            "masked_pan": card.masked_pan,
            "card_type": getattr(card.card_type, "value", card.card_type),
            "status": getattr(card.status, "value", card.status),
        }), 201
