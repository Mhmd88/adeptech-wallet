from __future__ import annotations
from flask import Blueprint, request, jsonify
from decimal import Decimal, ROUND_HALF_UP

import app
from app.models import Card, Balance, AuthHold, CardStatus

bp = Blueprint("auth_webhook", __name__)

ISO_TO_CCY = {"840": "USD", "422": "LBP"}

def _to_minor(amount_str: str) -> int:
    # Parse safely: "59.99" -> 5999 as int, no float drift
    d = Decimal(str(amount_str)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return int(d * 100)

@bp.post("/authorization")
def authorize_card():
    req = request.get_json(silent=True) or {}

    pan = (req.get("primaryAccountNumber") or "").strip()
    currency_code = str(req.get("currencyCode") or "").strip()
    amount_str = str(req.get("amountTransaction") or "0").strip()
    idem = (req.get("idempotency_key") or "").strip()

    # Basic input validation
    if not pan or not currency_code:
        return _decline(req, "missing_pan_or_currency")

    try:
        amount_minor = _to_minor(amount_str)
    except Exception:
        return _decline(req, "invalid_amount_format")

    if amount_minor <= 0:
        return _decline(req, "invalid_amount")

    ccy = ISO_TO_CCY.get(currency_code)
    if not ccy:
        return _decline(req, "unsupported_currency")

    with app.SessionLocal() as session:
        # Find card by masked PAN
        card = session.query(Card).filter_by(masked_pan=pan).first()
        if not card:
            return _decline(req, "card_not_found")
        if card.status != CardStatus.active:
            return _decline(req, "card_inactive")

        # Balance lookup
        bal = session.query(Balance).filter_by(user_id=card.user_id, currency=ccy).first()
        if not bal:
            return _decline(req, "no_balance_for_currency")

        # FUNDS CHECK
        available = int(bal.available_minor or 0)
        if available < amount_minor:
            return _decline(req, "insufficient_funds")

        # Reserve funds (approve path)
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

        return _approve(req, new_balance_minor=bal.available_minor, approval_code=hold.id)

def _base_response(req):
    return {
        "messageType": "2110",
        "primaryAccountNumber": req.get("primaryAccountNumber"),
        "processingCode": req.get("processingCode"),
        "amountTransaction": req.get("amountTransaction"),
        "amountCardholderBilling": req.get("amountCardholderBilling"),
        "dateAndTimeTransmission": req.get("dateAndTimeTransmission"),
        "conversionRateCardholderBilling": req.get("conversionRateCardholderBilling"),
        "systemsTraceAuditNumber": req.get("systemsTraceAuditNumber"),
        "dateCapture": req.get("dateCapture"),
        "merchantCategoryCode": req.get("merchantCategoryCode"),
        "acquiringInstitutionIdentificationCode": req.get("acquiringInstitutionIdentificationCode"),
        "retrievalReferenceNumber": req.get("retrievalReferenceNumber"),
        "cardAcceptorTerminalIdentification": req.get("cardAcceptorTerminalIdentification"),
        "cardAcceptorIdentificationCode": req.get("cardAcceptorIdentificationCode"),
        "cardAcceptorName": req.get("cardAcceptorName"),
        "cardAcceptorCity": req.get("cardAcceptorCity"),
        "cardAcceptorCountryCode": req.get("cardAcceptorCountryCode"),
    }

def _approve(req, new_balance_minor: int, approval_code: str):
    resp = _base_response(req)
    resp.update({
        "actionCode": "000",
        "approvalCode": approval_code,
        "additionalAmounts": [{
            "accountType": "00",
            "amountType": "02",
            "currencyCode": req.get("currencyCode"),
            "currencyMinorUnit": "2",
            "amountSign": "C",
            "value": str(int(new_balance_minor)).zfill(12),
        }],
    })
    return jsonify(resp), 200

def _decline(req, reason: str):
    resp = _base_response(req)
    resp.update({
        "actionCode": "005",
        "approvalCode": "000000",
        "declineReason": reason,
    })
    return jsonify(resp), 200
