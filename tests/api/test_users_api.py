import json
from app import create_app
from app.models import Base

def test_create_user_seeds_balances():
    app = create_app(testing=True)
    client = app.test_client()

    res = client.post("/v1/users/", data=json.dumps({
        "email": "apiuser@example.com",
        "full_name": "API User",
        "password": "secret"
    }), content_type="application/json")

    assert res.status_code == 201
    body = res.get_json()
    assert body["email"] == "apiuser@example.com"
    # has both USD & LBP balances
    codes = sorted([b["code"] for b in body["balances"]])
    assert codes == [422, 840]
