from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Stock(Base):
    __tablename__ = "stocks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id = Mapped[int] = mapped_column(Integer, ForeignKey("drinks.id"), nullable = False)
    warehouse_id = Mapped[int] = mapped_column(Integer, ForeignKey("warehouses.id"), nullable = False)
    quantity: Mapped[int] = mapped_column(Integer, gt = -1)
    reserved_quantity = Mapped[int] = mapped_column(Integer, gt = -1)

    ... #relationships