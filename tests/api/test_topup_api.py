import json
from app import create_app

def test_topup_endpoint_increments_balance():
    app = create_app(testing=True)
    client = app.test_client()

    # create user first
    client.post("/v1/users/", data=json.dumps({
        "email": "seed@example.com", "full_name": "Seed", "password": "x"
    }), content_type="application/json")

    # top up USD twice
    r1 = client.post("/v1/balances/topup", data=json.dumps({
        "email": "seed@example.com", "currency": "USD", "amount_minor": 150
    }), content_type="application/json")
    assert r1.status_code == 200
    assert r1.get_json()["new_available_minor"] == 150

    r2 = client.post("/v1/balances/topup", data=json.dumps({
        "email": "seed@example.com", "currency": "USD", "amount_minor": 50
    }), content_type="application/json")
    assert r2.status_code == 200
    assert r2.get_json()["new_available_minor"] == 200
