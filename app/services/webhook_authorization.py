from decimal import Decimal, ROUND_HALF_UP
from app.models import Card, Balance, AuthHold, CardStatus
from app import SessionLocal


ISO_TO_CCY = {"840": "USD", "422": "LBP"}


class AuthorizationError(Exception):...
class MissingPanOrCurrency(AuthorizationError):...
class InvalidAmountFormat(AuthorizationError):...
class InvalidAmountValue(AuthorizationError):...
class UnsupportedCurrency(AuthorizationError):...
class CardNotFound(AuthorizationError):...
class CardInactive(AuthorizationError):...
class NoBalanceForCurrency(AuthorizationError):...
class InsufficientFunds(AuthorizationError):...


def _to_minor(amount_str: str) -> int:
    d = Decimal(str(amount_str)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)


def authorize_transaction(payload: dict):
    """
    Returns (AuthHold, new_balance_minor) on success.
    """
    pan = (payload.get("primaryAccountNumber") or "").strip()
    currency_code = str(payload.get("currencyCode") or "").strip()
    amount_str = str(payload.get("amountTransaction") or "0").strip()
    idem = (payload.get("idempotency_key") or "").strip()

    if not pan or not currency_code:
        raise MissingPanOrCurrency("missing_pan_or_currency")

    try:
        amount_minor = _to_minor(amount_str)
    except Exception:
        raise InvalidAmountFormat("invalid_amount_format")

    if amount_minor <= 0:
        raise InvalidAmountValue("invalid_amount")

    ccy = ISO_TO_CCY.get(currency_code)
    if not ccy:
        raise UnsupportedCurrency("unsupported_currency")

    with SessionLocal() as session:
     
        card = session.query(Card).filter_by(masked_pan=pan).first()
        if not card:
            raise CardNotFound("card_not_found")

        if card.status != CardStatus.active:
            raise CardInactive("card_inactive")

        bal = session.query(Balance).filter_by(user_id=card.user_id, currency=ccy).first()
        if not bal:
            raise NoBalanceForCurrency("no_balance_for_currency")

        available = int(bal.available_minor or 0)
        if available < amount_minor:
            raise InsufficientFunds("insufficient_funds")

        bal.available_minor = available - amount_minor
        hold = AuthHold(
            user_id=card.user_id,
            card_id=card.id,
            currency=ccy,
            amount_minor=amount_minor,
            idempotency_key=idem or None,
        )
        session.add(hold)
        session.commit()

        return hold, bal.available_minor
