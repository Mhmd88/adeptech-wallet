from __future__ import annotations

import enum, uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, Integer, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional


from .base import Base

if TYPE_CHECKING:
    from .user import User

class TxnType(str, enum.Enum):
    P2P = "P2P"
    TOPUP = "TOPUP"         # nice to log seed top-ups too
    AUTH_HOLD = "AUTH_HOLD" # optional: when you add webhook holds

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Actors (for TOPUP you can leave from_user_id NULL)
    from_user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    to_user_id:   Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Money & currency
    currency: Mapped[str] = mapped_column(String(3))        # "USD" | "LBP"
    currency_code: Mapped[int] = mapped_column(Integer)     # 840 | 422
    amount_minor: Mapped[int] = mapped_column(BigInteger)   # positive integer

    # Classification / safety
    type: Mapped[TxnType] = mapped_column(default=TxnType.P2P)
    idempotency_key: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)

    # (Optional) ORM links for convenience
    from_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[from_user_id])
    to_user: Mapped[Optional["User"]] = relationship("User", foreign_keys=[to_user_id])

    def __repr__(self) -> str:
        return f"<Txn {self.type} {self.amount_minor} {self.currency} from={self.from_user_id} to={self.to_user_id}>"
