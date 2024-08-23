from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from sqlalchemy.types import Numeric, String, LargeBinary, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
import datetime
from dataclasses import dataclass

Base = declarative_base()

######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######


@dataclass
class Events(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    timestamp: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True))
    type: Mapped[str] = mapped_column(String)
    event: Mapped[str] = mapped_column(String)
    message: Mapped[bytes] = mapped_column(LargeBinary)


######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######
