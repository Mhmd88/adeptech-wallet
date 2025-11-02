from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User, Balance, Transaction, TxnType

# Domain Exceptions
class TransferError(Exception):...
class UnsupportedCurrency(TransferError):...
class InvalidAmount(TransferError):...
class UserNotFound(TransferError):...
class BalanceNotFound(TransferError):...
class InsufficientFunds(TransferError):...
class DuplicateTransfer(TransferError):...

CODES = {"USD": 840, "LBP": 422}

# Service API
def p2p_transfer(
    session: Session,
    from_email: str,
    to_email: str,
    currency: str,
    amount_minor: int,
    idem: Optional[str] = None,
) -> Transaction:
    
    fe = (from_email or "").strip().lower()
    te = (to_email or "").strip().lower()
    ccy = (currency or "").strip().upper()

    #Validate inputs
    if not fe or not te:
        raise UserNotFound("from/to user must be provided")
    if fe == te:
        raise InvalidAmount("cannot transfer to self")
    if ccy not in CODES:
        raise UnsupportedCurrency(f"unsupported currency: {ccy}")
    if not isinstance(amount_minor, int):
        raise InvalidAmount("amount must be provided in integer minor units")
    if amount_minor <= 0:
        raise InvalidAmount("amount must be > 0")

    #Lookup users 
    src: Optional[User] = session.query(User).filter_by(email=fe).first()
    dst: Optional[User] = session.query(User).filter_by(email=te).first()
    if not src or not dst:
        raise UserNotFound("from/to user not found")

    if idem:
        existing: Optional[Transaction] = (
            session.query(Transaction).filter_by(idempotency_key=idem).first()
        )
        if existing:
            same = (
                existing.type == TxnType.P2P and
                existing.currency == ccy and
                existing.amount_minor == amount_minor and
                existing.from_user_id == src.id and
                existing.to_user_id == dst.id
            )
            if same:
                return existing
            raise DuplicateTransfer("idempotency key already used for a different transfer")

    sbal: Optional[Balance] = (
        session.query(Balance)
        .filter_by(user_id=src.id, currency=ccy)
        .with_for_update()
        .first()
    )
    dbal: Optional[Balance] = (
        session.query(Balance)
        .filter_by(user_id=dst.id, currency=ccy)
        .with_for_update()
        .first()
    )
    if not sbal or not dbal:
        raise BalanceNotFound("missing balance for one of the users")

    # Funds check 
    current = int(sbal.available_minor or 0)
    if current < amount_minor:
        raise InsufficientFunds("insufficient funds")

    try:
        sbal.available_minor = current - amount_minor
        dbal.available_minor = int(dbal.available_minor or 0) + amount_minor

        txn = Transaction(
            from_user_id=src.id,
            to_user_id=dst.id,
            currency=ccy,
            currency_code=CODES[ccy],
            amount_minor=amount_minor,
            type=TxnType.P2P,
            idempotency_key=idem,
        )
        session.add(txn)
        session.commit()
        session.refresh(txn)
        return txn

    except IntegrityError:
        session.rollback()
        raise DuplicateTransfer("duplicate transfer (idempotency)")
