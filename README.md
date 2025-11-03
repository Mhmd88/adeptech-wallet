# adeptech-wallet
🏦 Adeptech Wallet — Flask + Postgres 
Overview

This project implements a minimal e-wallet system using Flask and PostgreSQL, covering:

✅ Account creation (users with balances in USD & LBP)

✅ Balance top-up endpoint for testing/demo

✅ P2P transfers between users in the same currency

✅ Card issuance (physical/virtual)

✅ Card authorization webhook (approve/decline logic)

⚙️ Setup Instructions
1️⃣ Clone and install dependencies
git clone (https://github.com/Mhmd88/adeptech-wallet)
cd adeptech_wallet
python -m venv venv
venv\Scripts\activate      
pip install -r requirements.txt

2️⃣ Configure environment

Create a .env file with:

DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/adeptech


Then create and migrate the database:

createdb adeptech
flask db upgrade

3️⃣ Run the app
flask run


Server will start on http://localhost:5000.

🧪 API Endpoints
👤 1. Create User

POST /v1/users/

{
  "email": "alice@example.com",
  "full_name": "Alice A.",
  "password": "pw"
}


✅ Initializes balances in USD (840) and LBP (422).

💰 2. Top-Up Balance

POST /v1/balances/topup

{
  "email": "alice@example.com",
  "currency": "USD",
  "amount_minor": 10000
}

🔄 3. P2P Transfer

POST /v1/p2p/transfer

{
  "from_email": "alice@example.com",
  "to_email": "bob@example.com",
  "currency": "USD",
  "amount": "12.34"
}

💳 4. Create Card

POST /v1/cards/

{
  "email": "alice@example.com",
  "masked_pan": "555555******9999",
  "type": "VIRTUAL",
  "status": "active"
}

🧾 5. Card Authorization Webhook

POST /v1/webhooks/authorization

✅ Approve
{
  "primaryAccountNumber": "555555******9999",
  "currencyCode": "840",
  "amountTransaction": "12.00",
  "idempotency_key": "auth-approve-001"
}


Response:

{
  "actionCode": "000",
  "approvalCode": "<uuid>"
}

❌ Decline
{
  "primaryAccountNumber": "555555******9999",
  "currencyCode": "840",
  "amountTransaction": "999999.00",
  "idempotency_key": "auth-decline-overspend"
}


Response:

{
  "actionCode": "005",
  "declineReason": "insufficient_funds"
}


💻 PowerShell Quick Commands to simulate a real situation
 
# Create users
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/v1/users/" -ContentType "application/json" -Body (@{ email="alice@example.com"; full_name="Alice"; password="pass" } | ConvertTo-Json -Compress)
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/v1/users/" -ContentType "application/json" -Body (@{ email="bob@example.com"; full_name="Bob"; password="pass" } | ConvertTo-Json -Compress)

# Top up Alice
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/v1/balances/topup" -ContentType "application/json" -Body (@{ email="alice@example.com"; currency="USD"; amount_minor=10000 } | ConvertTo-Json -Compress)

# Transfer $12.34 from Alice → Bob
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/v1/p2p/transfer" -ContentType "application/json" -Headers @{ "Idempotency-Key"="p2p-demo-001" } -Body (@{ from="alice@example.com"; to="bob@example.com"; currency="USD"; amount="12.34" } | ConvertTo-Json -Compress)

# Create a virtual card
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/v1/cards/" -ContentType "application/json" -Body (@{ email="alice@example.com"; masked_pan="555555******9999"; type="VIRTUAL"; status="active" } | ConvertTo-Json -Compress)

# Webhook authorization test
Invoke-RestMethod -Method POST -Uri "http://localhost:5000/v1/webhooks/authorization" -ContentType "application/json" -Body (@{ primaryAccountNumber="555555******9999"; currencyCode="840"; amountTransaction="12.00"; idempotency_key="auth-approve-001" } | ConvertTo-Json -Compress)


🧩 Architecture

services/ — core business logic

routes/ — Flask blueprints per resource

models/ — SQLAlchemy models

migrations/ — Alembic migrations

tests/ — pytest API tests
