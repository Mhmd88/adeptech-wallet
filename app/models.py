from sqlalchemy import Integer, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base




class User(Base):
 __tablename__ = "users"


# Use string UUIDs for simplicity (portable across SQLite/Postgres)
id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

# Minimal profile fields for now
email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
full_name: Mapped[str] = mapped_column(String(255))
password_hash: Mapped[str] = mapped_column(String(255), default="")
created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
balances: Mapped[list["Balance"]] = relationship(
    back_populates="user", cascade="all, delete-orphan"
)

def __repr__(self) -> str:
 return f"<User id={self.id} email={self.email}>"



class Balance(Base):
    __tablename__ = "balances"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"))

    currency: Mapped[str] = mapped_column(String(3))        # "USD" | "LBP"
    currency_code: Mapped[int] = mapped_column(Integer)     # 840 | 422
    available_minor: Mapped[int] = mapped_column(BigInteger, default=0)

    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="balances")

    __table_args__ = (UniqueConstraint("user_id", "currency", name="uq_user_currency"),)

    def __repr__(self):
        return f"<Balance user={self.user_id} {self.currency}={self.available_minor}>"

