from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

import app
from app.models import Card, Balance, AuthHold, CardStatus

ISO_TO_CCY = {"840": "USD", "422": "LBP"}

class AuthorizationError(Exception): ...

def _to_minor(amount_str: str) -> int:
    d = Decimal(str(amount_str)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)

def authorize_transaction(req: dict) -> Tuple[AuthHold, int]:
    pan = (req.get("primaryAccountNumber") or "").strip()
    ccy_code = str(req.get("currencyCode") or "").strip()
    amount_str = str(req.get("amountTransaction") or "0").strip()
    idem = (req.get("idempotency_key") or "").strip() or None

    if not pan or not ccy_code:
        raise AuthorizationError("missing_pan_or_currency")

    try:
        amount_minor = _to_minor(amount_str)
    except Exception:
        raise AuthorizationError("invalid_amount_format")
    if amount_minor <= 0:
        raise AuthorizationError("invalid_amount")

    ccy = ISO_TO_CCY.get(ccy_code)
    if not ccy:
        raise AuthorizationError("unsupported_currency")

    with app.SessionLocal() as session:
        # Look up card & ensure it's active
        card = session.query(Card).filter_by(masked_pan=pan).first()
        if not card:
            raise AuthorizationError("card_not_found")
        if card.status != CardStatus.active:
            raise AuthorizationError("card_inactive")

        # Get the user's balance for the given currency
        bal = session.query(Balance).filter_by(user_id=card.user_id, currency=ccy).first()
        if not bal:
            raise AuthorizationError("no_balance_for_currency")

        # ── Critical for tests using a different session: ensure the freshest row.
        # In unit tests, the balance may be edited/committed in a separate session.
        session.refresh(bal)

        # Strict funds check
        try:
            available = int(bal.available_minor or 0)
        except Exception:
            available = 0

        if available < amount_minor:
            raise AuthorizationError("insufficient_funds")

        # Reserve funds (approve)
        bal.available_minor = available - amount_minor
        hold = AuthHold(
            user_id=card.user_id,
            card_id=card.id,
            currency=ccy,
            amount_minor=amount_minor,
            idempotency_key=idem
        )
        session.add(hold)
        session.commit()

        return hold, int(bal.available_minor)
