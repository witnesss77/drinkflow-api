from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import UniqueConstraint
from typing import List
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class Drink(Base):
    __tablename__ = "drinks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    desc: Mapped[str] = mapped_column(String(100), nullable=False)
    alcoholic: Mapped[bool] = mapped_column(Boolean, nullable=False)
    price: Mapped[int] = mapped_column(Integer)
    factory_id: Mapped[int] = mapped_column(ForeignKey("factories.id"), nullable=False)

    factory: Mapped["Factory"] = relationship(back_populates="drinks")
    stock: Mapped[List["Stock"]] = relationship(back_populates="drink")
    items: Mapped["OrderItem"] = relationship(back_populates="drinks")


class Factory(Base):
    __tablename__ = "factories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location: Mapped[str] = mapped_column(String(100), nullable=False)
    
    drinks: Mapped[List["Drink"]] = relationship(back_populates="factory")


class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    drink_id: Mapped[int] = mapped_column(Integer, ForeignKey("drinks.id"), nullable = False)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable = False)
    quantity: Mapped[int] = mapped_column(Integer)
    reserved_quantity: Mapped[int] = mapped_column(Integer)

    drink: Mapped["Drink"] = relationship(back_populates="stock")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="stocks")

    __table_args__ = (
    UniqueConstraint("drink_id", "warehouse_id", name="uq_stock_drink_warehouse"),
)
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    email: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20))

    orders: Mapped[List["Order"]] = relationship(back_populates="user")

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
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("orders.id"), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    drink_id: Mapped[int] = mapped_column(Integer, ForeignKey("drinks.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_item: Mapped[int] = mapped_column(Integer, nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
    drinks: Mapped["Drink"] = relationship(back_populates="items")


class Warehouse(Base):
    __tablename__ = "warehouses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(100))

    stocks: Mapped[List["Stock"]] = relationship(back_populates="warehouse")
    orders: Mapped[List["Order"]] = relationship(back_populates="warehouse")