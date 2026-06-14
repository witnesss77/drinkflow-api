from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from orders import Order
from stock import Stock

class Base(DeclarativeBase):
    pass

class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(100))

    stocks: Mapped[List["Stock"]] = relationship(back_populates="warehouse")
    orders: Mapped[List["Order"]] = relationship(back_populates="orders")