from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Drink(Base):
    __table_name__ = "drinks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    desc: Mapped[str] = mapped_column(String(100), nullable=False)
    alcoholic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    price: Mapped[int] = mapped_column(Integer, gt = 0)
    quantity: Mapped[int] = mapped_column(Integer, gt = -1)
    factory_id: Mapped[int] = ...

    ... #relationships