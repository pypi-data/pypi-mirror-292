from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric, String
from sqlalchemy import ForeignKey

from dataclasses import dataclass

Base = declarative_base()


######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######
@dataclass
class Account(Base):
    __tablename__ = "account"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)

    portfolio: Mapped[list["portfolio"]] = relationship(
        "Portfolio", primaryjoin="foreign(Portfolio.account_id) == Account.id"
    )

    # Value given to this account
    value: Mapped[float] = mapped_column(Numeric(10, 2))


@dataclass
class AccountTransaction(Base):
    __tablename__ = "account_transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))
    from_location: Mapped[str] = mapped_column(String(30))
    to_location: Mapped[str] = mapped_column(String(30))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))


######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######
