from typing import List
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class SuperFamily(Base):
    __tablename__ = "super_families"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    sub_order_id: Mapped[int] = mapped_column(ForeignKey("sub_orders.id"))
    sub_order: Mapped["SubOrder"] = relationship(back_populates="super_families")
    families: Mapped[List["Family"]] = relationship(back_populates="super_family")

    def __init__(self, name, sub_order):
        self.name = name
        self.sub_order = sub_order

    def __repr__(self):
        return f"<SuperFamily name={self.name}>"
