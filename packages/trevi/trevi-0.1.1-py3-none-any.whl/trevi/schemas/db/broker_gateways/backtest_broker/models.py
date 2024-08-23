from sqlalchemy.orm import declarative_base, Mapped, mapped_column
from sqlalchemy.types import LargeBinary, String

from dataclasses import dataclass

Base = declarative_base()

######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######


@dataclass
class Order(Base):
    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[bytes] = mapped_column(LargeBinary)
    status: Mapped[str] = mapped_column(String(30))


######>>>>>>>>>>>>>>>>>>>>>>> TABLES <<<<<<<<<<<<<<<<<<<<<<<<######
