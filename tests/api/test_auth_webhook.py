import json
from app.models import User, Balance, Card, AuthHold, CardStatus

def setup_user_and_card(session):
    user = User(email="carduser@example.com", full_name="Card User", password_hash="hash")
    session.add(user); session.flush()
    session.add(Balance(user_id=user.id, currency="USD", currency_code=840, available_minor=10000))
    card = Card(user_id=user.id, masked_pan="545454******5454", type="virtual", status=CardStatus.active)
    session.add(card); session.commit()
    return user, card

def test_retail_authorization_approve(tmp_path):
    db_url = f"sqlite:///{tmp_path/'t1.db'}"
    from app import create_app
    app = create_app(testing=True, database_url=db_url)
    client = app.test_client()

    import app
    with app.SessionLocal() as s:
        user, _ = setup_user_and_card(s)

    # REAL payload dict (retail)
    payload = {
        "messageType": "0100",
        "processingCode": "000000",
        "primaryAccountNumber": "545454******5454",
        "amountTransaction": "27.50",
        "amountCardholderBilling": "27.50",
        "dateAndTimeTransmission": "2025-10-26T13:04:15Z",
        "conversionRateCardholderBilling": "1.000000",
        "systemsTraceAuditNumber": "847392",
        "dateCapture": "2025-10-26",
        "merchantCategoryCode": "5411",
        "acquiringInstitutionIdentificationCode": "ACQ001",
        "retrievalReferenceNumber": "012345678901",
        "cardAcceptorTerminalIdentification": "T98765",
        "cardAcceptorIdentificationCode": "MRC123",
        "cardAcceptorName": "SuperMart Downtown",
        "cardAcceptorCity": "Beirut",
        "cardAcceptorCountryCode": "422",
        "entry_mode": "chip",
        "currencyCode": "840",
        "txn_ref": "BANK_TXN_001122",
        "idempotency_key": "demo-approve"
    }

    res = client.post("/v1/webhooks/authorization", json=payload)
    body = res.get_json()
    assert res.status_code == 200
    assert body["actionCode"] == "000"

    with app.SessionLocal() as s:
        bal = s.query(Balance).filter_by(user_id=user.id, currency="USD").first()
        assert bal.available_minor == 10000 - 2750
        assert s.query(AuthHold).count() == 1

def test_ecommerce_decline_for_insufficient_funds(tmp_path):
    db_url = f"sqlite:///{tmp_path/'t2.db'}"
    from app import create_app
    app = create_app(testing=True, database_url=db_url)
    client = app.test_client()

    import app
    with app.SessionLocal() as s:
        user, _ = setup_user_and_card(s)
        user_id = user.id
        bal = s.query(Balance).filter_by(user_id=user_id, currency="USD").first()
        bal.available_minor = 100  # $1.00
        s.commit()

    # REAL payload dict (e-commerce)
    payload = {
        "messageType": "0100",
        "processingCode": "000000",
        "primaryAccountNumber": "545454******5454",
        "amountTransaction": "59.99",
        "amountCardholderBilling": "59.99",
        "dateAndTimeTransmission": "2025-10-26T13:07:03Z",
        "conversionRateCardholderBilling": "1.000000",
        "systemsTraceAuditNumber": "847393",
        "merchantCategoryCode": "5732",
        "acquiringInstitutionIdentificationCode": "ACQ007",
        "retrievalReferenceNumber": "012345678902",
        "cardAcceptorIdentificationCode": "ECM456",
        "cardAcceptorName": "Acme Online",
        "cardAcceptorCity": "Beirut",
        "cardAcceptorCountryCode": "422",
        "currencyCode": "840",
        "ecom": {
            "avs_result": "Y",
            "three_ds": "frictionless",
            "ip_address": "203.0.113.24",
            "channel": "web"
        },
        "txn_ref": "BANK_TXN_001123",
        "idempotency_key": "demo-decline"
    }

    res = client.post("/v1/webhooks/authorization", json=payload)
    body = res.get_json()
    assert res.status_code == 200
    assert body["actionCode"] == "005"
    assert body["approvalCode"] == "000000"

    with app.SessionLocal() as s:
        bal = s.query(Balance).filter_by(user_id=user_id, currency="USD").first()
        assert bal.available_minor == 100
        assert s.query(AuthHold).count() == 0
