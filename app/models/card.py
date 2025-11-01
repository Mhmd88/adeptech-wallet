from __future__ import annotations

import enum, uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class CardType(enum.Enum):
    PHYSICAL = "PHYSICAL"
    VIRTUAL = "VIRTUAL"

class CardStatus(str, enum.Enum):
    active = "active"
    frozen = "frozen"
    cancelled = "cancelled"

if TYPE_CHECKING:
    from .user import User

class Card(Base):
    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))

    masked_pan: Mapped[str] = mapped_column(String(19))            # e.g., "545454******5454"
    
    card_type: Mapped[CardType] = mapped_column(SAEnum(CardType), nullable=False)

    status: Mapped[CardStatus] = mapped_column(SAEnum(CardStatus), default=CardStatus.active)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="cards")

    def __repr__(self):
        return f"<Card id={self.id} user={self.user_id} status={self.status}>"
