from sqlalchemy import Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Order(Base):
    __table_name__ = "orders"
    ...


class OrderItem(Base):
    __table_name__ = "order_items"
    ...
