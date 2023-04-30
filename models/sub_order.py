from typing import List
from sqlalchemy import Integer, String
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from models.base import Base


class SubOrder(Base):
    __tablename__ = "sub_orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    super_families: Mapped[List["SuperFamily"]] = relationship(
        back_populates="sub_order"
    )

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<SubOrder name={self.name}>"
