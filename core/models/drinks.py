from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, UniqueConstraint
from typing import List
from factories import Factory
from orders import OrderItem
from stock import Stock

class Base(DeclarativeBase):
    pass

class Drink(Base):
    __tablename__ = "drinks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    desc: Mapped[str] = mapped_column(String(100), nullable=False)
    alcoholic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    price: Mapped[int] = mapped_column(Integer, gt = 0)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id"), nullable=False)

    factory: Mapped["Factory"] = relationship(back_populates="drinks")
    stock: Mapped[List["Stock"]] = relationship(back_populates="drink")
    items = Mapped["OrderItem"] = relationship(back_populates="drinks")