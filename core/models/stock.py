from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, UniqueConstraint
from typing import List
from drinks import Drink
from warehouse import Warehouse

class Base(DeclarativeBase):
    pass

class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    drink_id :Mapped[int] = mapped_column(Integer, ForeignKey("drinks.id"), nullable = False)
    warehouse_id: Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable = False)
    quantity: Mapped[int] = mapped_column(Integer, gt = -1)
    reserved_quantity: Mapped[int] = mapped_column(Integer, gt = -1)

    drink: Mapped["Drink"] = relationship(back_populates="stock")
    warehouse: Mapped["Warehouse"] = relationship(back_populates="stocks")

    __table_args__ = (
    UniqueConstraint("drink_id", "warehouse_id", name="uq_stock_drink_warehouse"),
)