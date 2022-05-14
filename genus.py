from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from base import Base


class Genus(Base):
    __tablename__ = "genera"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    family_id = Column(ForeignKey("families.id"))
    family = relationship("Family", backref=backref("genera"))

    def __init__(self, name, family):
        self.name = name
        self.family = family

    def __repr__(self):
        return f"<Genus name={self.name}, family={self.family.name}>"
