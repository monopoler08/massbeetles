from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.base import Base


class SuperFamily(Base):
    __tablename__ = "super_families"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    sub_order_id = Column(ForeignKey("sub_orders.id"))
    sub_order = relationship("SubOrder", backref=backref("super_families"))

    def __init__(self, name, sub_order):
        self.name = name
        self.sub_order = sub_order

    def __repr__(self):
        return f"<SuperFamily name={self.name}>"
