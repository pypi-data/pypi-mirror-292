from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric, String
from sqlalchemy import ForeignKey

from dataclasses import dataclass

Base = declarative_base()

######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######


@dataclass
class Portfolio(Base):
    __tablename__ = "portfolio"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("account.id"))


@dataclass
class PortfolioTransaction(Base):
    __tablename__ = "portfolio_transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolio.id"))
    from_location: Mapped[str] = mapped_column(String(30))
    to_location: Mapped[str] = mapped_column(String(30))
    amount: Mapped[float] = mapped_column(Numeric(10, 2))


######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######
