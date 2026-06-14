from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from typing import List
from users import User
from warehouse import Warehouse
from drinks import Drink


class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="created", nullable=False)
    is_paid: Mapped[bool] = mapped_column(Boolean, default=False)

    items: Mapped[List["OrderItem"]] = relationship(back_populates="order")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="orders")
    user: Mapped["User"] = relationship(back_populates="orders")

class OrderItem(Base):
    __tablename__ = "order_items"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    drink_id: Mapped[int] = mapped_column(Integer, ForeignKey("drinks.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_item: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    drinks: Mapped["Drink"] = relationship(back_populates="items")
