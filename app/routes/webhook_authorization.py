from __future__ import annotations

from flask import Blueprint, request, jsonify
from app.services.webhook_authorization import authorize_transaction, AuthorizationError

bp = Blueprint("auth_webhook", __name__)  

def _base_response(req: dict) -> dict:
    
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


@bp.post("/authorization")
def authorize_card():
    req = request.get_json(silent=True) or {}

    try:
        hold, new_balance_minor = authorize_transaction(req)
        resp = _base_response(req)
        resp.update({
            "actionCode": "000",
            "approvalCode": hold.id,
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

    except AuthorizationError as e:
        # Decline path (insufficient funds, inactive card, bad payload, etc.)
        resp = _base_response(req)
        resp.update({
            "actionCode": "005",
            "approvalCode": "000000",
            "declineReason": str(e),
        })
        return jsonify(resp), 200
