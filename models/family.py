from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from models.base import Base


class Family(Base):
    __tablename__ = "families"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    super_family_id = Column(ForeignKey("super_families.id"))
    super_family = relationship("SuperFamily", backref=backref("families"))

    def __init__(self, name, super_family):
        self.name = name
        self.super_family = super_family

    def __repr__(self):
        return f"<Family name={self.name} super_family={self.super_family.name}>"
