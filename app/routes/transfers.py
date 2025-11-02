from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from flask import Blueprint, request, jsonify

import app
from app.services.transfers import (
    p2p_transfer,
    TransferError,
    UnsupportedCurrency,
    InvalidAmount,
    UserNotFound,
    BalanceNotFound,
    InsufficientFunds,
    DuplicateTransfer,
)

bp = Blueprint("p2p", __name__) 

def _to_minor(amount_str: str) -> int:
    # Safe: "12.34" -> 1234
    d = Decimal(str(amount_str or "0")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)

@bp.post("/transfer")
def transfer():
    payload = request.get_json(silent=True) or {}

    # Accept idempotency from body or header =
    idem = (payload.get("idempotency_key") or request.headers.get("Idempotency-Key") or "").strip() or None

    from_email = (payload.get("from") or payload.get("from_email") or "").strip().lower()
    to_email   = (payload.get("to") or payload.get("to_email") or "").strip().lower()
    currency   = (payload.get("currency") or "").strip().upper()
    amount_raw = str(payload.get("amount") or "").strip()

    # Minimal parsing; domain validation happens in the service
    try:
        amount_minor = _to_minor(amount_raw)
    except Exception:
        return _err("invalid amount format"), 400

    with app.SessionLocal() as session:
        try:
            txn = p2p_transfer(
                session=session,
                from_email=from_email,
                to_email=to_email,
                currency=currency,
                amount_minor=amount_minor,
                idem=idem,
            )
            return jsonify({
                "transaction_id": txn.id,
                "type": txn.type.name if hasattr(txn.type, "name") else "P2P",
                "currency": txn.currency,
                "currency_code": txn.currency_code,
                "amount_minor": txn.amount_minor,
                "from_user_id": txn.from_user_id,
                "to_user_id": txn.to_user_id,
                "idempotency_key": txn.idempotency_key,
            }), 201

        except (InvalidAmount, UnsupportedCurrency, UserNotFound, BalanceNotFound) as e:
            return _err(str(e)), 400
        except InsufficientFunds as e:
            return _err(str(e)), 409
        except DuplicateTransfer as e:
            return _err(str(e)), 409
        except TransferError as e:
            return _err(str(e)), 400
        except Exception:
            # Unexpected
            return _err("internal error"), 500

def _err(msg: str):
    return {"error": msg}
