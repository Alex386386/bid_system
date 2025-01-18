from datetime import datetime, timezone

from sqlalchemy import (
    Integer,
    String,
    Float,
    ForeignKey,
    text,
    BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from bets.enums import BetStatuses
from .db import Base


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(256), unique=True)
    username: Mapped[str] = mapped_column(
        String(256), comment="Никнейм пользователя", unique=True
    )
    password: Mapped[str] = mapped_column(String(256))

    create_date: Mapped[int] = mapped_column(
        BigInteger,
        default=lambda: int(datetime.now(timezone.utc).timestamp()),
        server_default=func.extract("epoch", func.now()),
    )
    update_date: Mapped[int] = mapped_column(
        BigInteger,
        default=lambda: int(datetime.now(timezone.utc).timestamp()),
        server_default=func.extract("epoch", func.now()),
        onupdate=func.extract("epoch", func.now()),
    )
    bets: Mapped[list["Bet"]] = relationship(
        "Bet", back_populates="user", cascade="all, delete-orphan"
    )


class Bet(Base):
    __tablename__ = "bets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bet_amount: Mapped[float] = mapped_column(Float)
    event_id: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(
        String,
        default=BetStatuses.NOT_PLAYED.value,
        server_default=text(f"'{BetStatuses.NOT_PLAYED.value}'"),
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            column="users.id",
            name="fk_user_id",
            ondelete="CASCADE",
        ),
        comment="ID Аккаунта",
        nullable=False,
        index=True,
    )
    user: Mapped["User"] = relationship("User", back_populates="bets")

    create_date: Mapped[int] = mapped_column(
        BigInteger,
        default=lambda: int(datetime.now(timezone.utc).timestamp()),
        server_default=func.extract("epoch", func.now()),
    )
    update_date: Mapped[int] = mapped_column(
        BigInteger,
        default=lambda: int(datetime.now(timezone.utc).timestamp()),
        server_default=func.extract("epoch", func.now()),
        onupdate=func.extract("epoch", func.now()),
    )
